from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db_utils.conn import get_db
from models import Task, User
from schemas import TaskCreate, TaskResponse, TaskUpdate
from loguru import logger
from app.email_utils import send_email_task
from dependencies import role_checker, get_current_user
from enums import UserRole
from typing import List, Optional
from config import USE_MAILING

router = APIRouter()


@router.post("/tasks/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task.creator_id = user.id
    return await Task.create_task(db, task)


@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> List[TaskResponse]:
    if user.role == UserRole.USER:
        return await Task.get_tasks_by_creator(db, user.id)
    return await Task.get_tasks(db)


@router.get("/tasks/{task_id}", response_model=Optional[TaskResponse])
async def get_task(
    task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    task = await Task.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.creator_id != user.id and user.role not in [
        UserRole.ADMIN,
        UserRole.MANAGER,
    ]:
        raise HTTPException(
            status_code=403, detail="You do not have access to this task"
        )
    return task


@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
)
async def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    existing_task = await Task.get_task_by_id(db, task_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if existing_task.creator_id != user.id and user.role not in [
        UserRole.ADMIN,
        UserRole.MANAGER,
    ]:
        raise HTTPException(
            status_code=403, detail="You do not have access to this task"
        )
    updated_task = await Task.update_task(db, task_id, task)
    if existing_task.status != updated_task.status and USE_MAILING is True:
        creator = await User.get_user_by_id(db, updated_task.creator_id)
        subject = f"Task {updated_task.name} status changed"
        message = f"Task {updated_task.name} status changed to {updated_task.status}"
        send_email_task(creator.email, subject, message)

    return updated_task


@router.delete(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    dependencies=[Depends(role_checker(UserRole.ADMIN, UserRole.MANAGER))],
)
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    return await Task.delete_task(db, task_id)
