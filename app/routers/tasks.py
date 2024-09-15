from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db_utils.conn import get_db
from models import Task
from schemas import TaskCreate, TaskResponse, TaskUpdate
from loguru import logger

router = APIRouter()


@router.post('/tasks/', response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    logger.info(f'Creating task: {task}')
    return await Task.create_task(db, task)


@router.get("/tasks", response_model=list[TaskResponse])
async def get_tasks(db: Session = Depends(get_db)):
    return await Task.get_tasks(db)


@router.get('/tasks/{task_id}', response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    return await Task.get_task_by_id(db, task_id)


@router.put('/tasks/{task_id}', response_model=TaskResponse)
async def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    return await Task.update_task(db, task_id, task)