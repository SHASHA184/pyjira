from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enums import TaskStatus, TaskPriority, UserRole


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    role: Optional[UserRole] = UserRole.USER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TaskResponse(BaseModel):
    id: int
    task_name: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    creator_id: int
    assignees: List[UserResponse]

    class Config:
        orm_mode = True


class TaskCreate(BaseModel):
    task_name: str
    description: Optional[str]
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    creator_id: int
    assignees: List[int]


class TaskUpdate(BaseModel):
    task_name: Optional[str]
    description: Optional[str]
    status: Optional[TaskStatus]
    priority: Optional[TaskPriority]
    creator_id: Optional[int]
    assignees: Optional[List[int]]
