from typing import List

import sqlalchemy.exc
from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.utils import password_hasher

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/", response_model=List[schemas.UserResponse])
async def get_all_users(db: Session = Depends(get_db)):
    all_users = db.query(models.User).all()
    return all_users


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def create_user(new_user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        hashed_password = password_hasher(new_user.password)
        new_user.password = hashed_password
        created_user = models.User(**new_user.dict())
        db.add(created_user)
        db.commit()
        db.refresh(created_user)
        return created_user
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"User with email: {new_user.email} already exists!")


@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found!")
    return user
