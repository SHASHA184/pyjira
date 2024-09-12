from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from db_utils.base_model import Base
import enum

# Статус задачі
class TaskStatus(str, enum.Enum):
    TODO = 'TODO'
    IN_PROGRESS = 'In progress'
    DONE = 'Done'

# Пріоритет задачі
class TaskPriority(str, enum.Enum):
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'

class UserRole(str, enum.Enum):
    ADMIN = 'Admin'
    USER = 'User'

# Таблиця для зв'язку Task і User (Many-to-Many)
task_user_table = Table(
    'task_user',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)

# Модель користувача
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)

# Модель задачі
class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(80), nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    creator = relationship("User", back_populates="created_tasks")
    assignees = relationship("User", secondary=task_user_table, back_populates="tasks")

# Відношення для користувача
User.created_tasks = relationship("Task", back_populates="creator")
User.tasks = relationship("Task", secondary=task_user_table, back_populates="assignees")
