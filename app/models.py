from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql.expression import select
from fastapi import HTTPException, status
from db_utils.base_model import Base
from security import hash_password, verify_password
from enums import TaskStatus, TaskPriority, UserRole
import sys
import pathlib
from typing import List, Optional

sys.path.append(str(pathlib.Path(__file__).resolve(strict=True).parent.parent))


from app.email_utils import send_email_task
from schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
)
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
    async def create_user(cls, db: Session, user: UserCreate) -> UserResponse:
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
    async def authenticate_user(
        cls, db: Session, user: UserLogin
    ) -> Optional[UserResponse]:
        query = select(cls).where(cls.username == user.username)
        result = await db.execute(query)
        db_user = result.scalars().first()

        if not db_user:
            return None

        if not verify_password(user.password, db_user.password):
            return None

        return UserResponse.model_validate(db_user)

    @classmethod
    async def get_user_by_id(cls, db: Session, user_id: int) -> Optional[UserResponse]:
        query = select(cls).where(cls.id == user_id)
        result = await db.execute(query)
        user = result.scalars().first()
        if not user:
            return None
        return UserResponse.model_validate(user)

    @classmethod
    async def get_user_by_username(
        cls, db: Session, username: str
    ) -> Optional[UserResponse]:
        query = select(cls).where(cls.username == username)
        result = await db.execute(query)
        user = result.scalars().first()
        if not user:
            return None
        return UserResponse.model_validate(user)

    @classmethod
    async def delete_user(cls, db: Session, user_id: int) -> Optional[UserResponse]:
        query = select(cls).where(cls.id == user_id)
        result = await db.execute(query)
        user = result.scalars().first()

        if not user:
            return None

        await user.delete(db)

        return user


# Модель задачі
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)

    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    creator = relationship("User", back_populates="created_tasks")
    assignees = relationship("User", secondary=task_user_table, back_populates="tasks")

    @classmethod
    async def create_task(cls, db: Session, task) -> TaskResponse:
        assignees_query = select(User).where(User.id.in_(task.assignees))
        assignees_result = await db.execute(assignees_query)
        assignees = assignees_result.scalars().all()

        new_task = cls(
            name=task.name,
            description=task.description,
            status=task.status,
            priority=task.priority,
            creator_id=task.creator_id,
            assignees=assignees,
        )

        await new_task.save(db)

        return TaskResponse.model_validate(new_task)

    @classmethod
    async def get_task_by_id(cls, db: Session, task_id: int) -> Optional[TaskResponse]:
        query = (
            select(cls).options(selectinload(cls.assignees)).where(cls.id == task_id)
        )
        result = await db.execute(query)
        task = result.scalars().first()
        if not task:
            return None
        return TaskResponse.model_validate(task)

    @classmethod
    async def get_tasks(cls, db: Session) -> List[TaskResponse]:
        query = select(cls).options(selectinload(cls.assignees))
        result = await db.execute(query)
        tasks = result.scalars().all()
        return [TaskResponse.model_validate(task) for task in tasks]

    @classmethod
    async def get_tasks_by_creator(
        cls, db: Session, creator_id: int
    ) -> List[TaskResponse]:
        query = (
            select(cls)
            .where(cls.creator_id == creator_id)
            .options(selectinload(cls.assignees))
        )
        result = await db.execute(query)
        tasks = result.scalars().all()
        return [TaskResponse.model_validate(task) for task in tasks]

    @classmethod
    async def update_task(cls, db: Session, task_id: int, task) -> TaskResponse:
        task_query = (
            select(cls).options(selectinload(cls.assignees)).where(cls.id == task_id)
        )
        task_result = await db.execute(task_query)
        existing_task = task_result.scalars().first()

        if not existing_task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Use the Base update method to update the fields
        await existing_task.update(
            db,
            name=task.name,
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

        return TaskResponse.model_validate(existing_task)

    @classmethod
    async def delete_task(cls, db: Session, task_id: int) -> Optional[TaskResponse]:
        query = select(cls).where(cls.id == task_id)
        result = await db.execute(query)
        task = result.scalars().first()

        if not task:
            return None

        await task.delete(db)

        return task


# Відношення для користувача
User.created_tasks = relationship("Task", back_populates="creator")
User.tasks = relationship("Task", secondary=task_user_table, back_populates="assignees")
