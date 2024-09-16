from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enums import TaskStatus, TaskPriority, UserRole


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    role: Optional[UserRole] = UserRole.USER


class UserLogin(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    creator_id: int
    assignees: List[UserResponse]

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    name: str
    description: Optional[str]
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    creator_id: Optional[int] = None
    assignees: List[int]


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignees: Optional[List[int]] = None

    class Config:
        from_attributes = True