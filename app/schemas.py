from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enums import TaskStatus, TaskPriority, UserRole

class UserOut(BaseModel):
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


class TaskOut(BaseModel):
    id: int
    task_name: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    creator_id: int
    assignees: List[UserOut]

    class Config:
        orm_mode = True


class TaskCreate(BaseModel):
    task_name: str
    description: Optional[str]
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    assignee_ids: List[int]

# Pydantic model for Task update (incoming data)
class TaskUpdate(BaseModel):
    task_name: Optional[str]
    description: Optional[str]
    status: Optional[TaskStatus]
    priority: Optional[TaskPriority]
    assignee_ids: Optional[List[int]]
