from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql.expression import select
from fastapi import HTTPException, status
from db_utils.base_model import Base
from security import hash_password, verify_password
from enums import TaskStatus, TaskPriority, UserRole
from schemas import UserCreate, UserLogin
from loguru import logger

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
        query = select(cls).where(cls.email == user.email)
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

        return True if db_user else False

    @classmethod
    async def get_user_by_email(cls, db: Session, email: str):
        query = select(cls).where(cls.email == email)
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_user_by_id(cls, db: Session, user_id: int):
        query = select(cls).where(cls.id == user_id)
        result = await db.execute(query)
        return result.scalars().first()


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


# Відношення для користувача
User.created_tasks = relationship("Task", back_populates="creator")
User.tasks = relationship("Task", secondary=task_user_table, back_populates="assignees")
