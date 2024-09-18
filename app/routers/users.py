from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db_utils.conn import get_db
from models import User
from schemas import UserCreate, UserResponse, UserLogin
from loguru import logger
from dependencies import role_checker
from enums import UserRole

# Initialize the APIRouter
router = APIRouter()


@router.post('/users/', response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return await User.create_user(db, user)

@router.get("/users/{user_id}", response_model=UserResponse, dependencies=[Depends(role_checker(UserRole.ADMIN, UserRole.MANAGER))])
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = await User.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/users/{user_id}", response_model=UserResponse, dependencies=[Depends(role_checker(UserRole.ADMIN))])
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    deleted = await User.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted