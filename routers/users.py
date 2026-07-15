from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Path, APIRouter
from pydantic import BaseModel, Field
try:
    from ..database import SessionLocal
    from ..models import Todo, Users
except ImportError:
    from database import SessionLocal
    from models import Todo, Users
from sqlalchemy.orm import Session
from starlette import status
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserVerification(BaseModel):
    password: str 
    new_password: str = Field(min_length=6)


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency,db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    return db.query(Users).filter(Users.id == user.get("id")).first()

@router.put('/password', status_code=status.HTTP_204_NO_CONTENT)
async def update_password(user_verification: UserVerification, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    
    db_user = db.query(Users).filter(Users.id == user.get("id")).first()
    
    if not bcrypt_context.verify(user_verification.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Error on password change. Please check your current password and try again.")
    
    db_user.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(db_user)
    db.commit()

class UserPhoneNumberUpdate(BaseModel):
    phone_number: str = Field(min_length=10, max_length=15)

@router.put('/phone_number/{phone_number}', status_code=status.HTTP_204_NO_CONTENT)
async def update_phone_number(phone_number: str, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    
    db_user = db.query(Users).filter(Users.id == user.get("id")).first()
    db_user.phone_number = phone_number
    db.add(db_user)
    db.commit()
