from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql.expression import select
from fastapi import HTTPException, status
from db_utils.base_model import Base
from security import hash_password, verify_password
from enums import TaskStatus, TaskPriority, UserRole
import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).resolve(strict=True).parent.parent))


from app.email_utils import send_email_task
from schemas import UserCreate, UserLogin, UserResponse
from loguru import logger
from sqlalchemy.orm import selectinload

# Таблиця для зв'язку Task і User (Many-to-Many)
task_user_table = Table(
    "task_user",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
)


# Модель користувача
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)

    @classmethod
    async def create_user(cls, db: Session, user: UserCreate):
        # Перевірка, чи існує користувач
        query = select(cls).where(cls.email == user.email)
        result = await db.execute(query)
        instance = result.scalars().first()

        if instance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered",
            )

        user.password = hash_password(user.password)
        new_user = cls(**user.model_dump())

        await new_user.save(db)

        return new_user

    @classmethod
    async def authenticate_user(cls, db: Session, user: UserLogin):
        query = select(cls).where(cls.username == user.username)
        result = await db.execute(query)
        db_user = result.scalars().first()

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not verify_password(user.password, db_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return UserResponse.model_validate(db_user)

    @classmethod
    async def get_user_by_id(cls, db: Session, user_id: int):
        query = select(cls).where(cls.id == user_id)
        result = await db.execute(query)
        return UserResponse.model_validate(result.scalars().first())

    @classmethod
    async def get_user_by_username(cls, db: Session, username: str):
        query = select(cls).where(cls.username == username)
        result = await db.execute(query)
        return UserResponse.model_validate(result.scalars().first())


# Модель задачі
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(80), nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)

    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    creator = relationship("User", back_populates="created_tasks")
    assignees = relationship("User", secondary=task_user_table, back_populates="tasks")

    @classmethod
    async def create_task(cls, db: Session, task):
        assignees_query = select(User).where(User.id.in_(task.assignees))
        assignees_result = await db.execute(assignees_query)
        assignees = assignees_result.scalars().all()

        new_task = cls(
            task_name=task.task_name,
            description=task.description,
            status=task.status,
            priority=task.priority,
            creator_id=task.creator_id,
            assignees=assignees,
        )

        await new_task.save(db)

        return new_task

    @classmethod
    async def get_task_by_id(cls, db: Session, task_id: int):
        query = (
            select(cls).options(selectinload(cls.assignees)).where(cls.id == task_id)
        )
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_tasks(cls, db: Session):
        query = select(cls).options(selectinload(cls.assignees))
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def update_task(cls, db: Session, task_id: int, task):
        task_query = (
            select(cls).options(selectinload(cls.assignees)).where(cls.id == task_id)
        )
        task_result = await db.execute(task_query)
        existing_task = task_result.scalars().first()

        if existing_task.status != task.status:
            creator = await User.get_user_by_id(db, existing_task.creator_id)
            creator_email = creator.email
            subject = f"Task status changed for {existing_task.task_name}"
            body = f"Task status has been changed from {existing_task.status} to {task.status}"
            send_email_task.delay(creator_email, subject, body)

        if not existing_task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Use the Base update method to update the fields
        await existing_task.update(
            db,
            task_name=task.task_name,
            description=task.description,
            status=task.status,
            priority=task.priority,
        )

        # Update the assignees if provided
        if task.assignees:
            assignees_query = select(User).where(User.id.in_(task.assignees))
            assignees_result = await db.execute(assignees_query)
            assignees = assignees_result.scalars().all()

            if len(assignees) != len(task.assignees):
                raise HTTPException(
                    status_code=400, detail="One or more assignees not found"
                )

            existing_task.assignees = assignees
            await existing_task.save(db)

        return existing_task


# Відношення для користувача
User.created_tasks = relationship("Task", back_populates="creator")
User.tasks = relationship("Task", secondary=task_user_table, back_populates="assignees")
