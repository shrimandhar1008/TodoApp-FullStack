from datetime import datetime, timedelta, timezone

from fastapi import Depends, APIRouter, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from ..database import SessionLocal
from ..models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

SECRET_KEY = "c1bf792e68430a6a8ce8c53bf4426d843cbc8937e596f2245d603145e348c0d5"  # Replace with your actual secret key
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
    email: str = Field(min_length=5)
    username: str = Field(min_length=3)
    phone_number: str = Field(min_length=10, max_length=15)  # New field for phone number
    password: str = Field(min_length=6)
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    password: str = Field(min_length=6)
    role: str = Field(min_length=3)  # New field for user role

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
templates = Jinja2Templates(directory="TodoApp/templates")

## pages  ##

@router.get("/login-page")
async def render_login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")

@router.get("/register-page")
async def render_register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")

### endpoints ###

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id:int, role: str, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    encoded_jwt = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        return {"username": username, "id": user_id, 'role': role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    existing_user = (
        db.query(Users)
        .filter(
            or_(
                Users.email == create_user_request.email,
                Users.username == create_user_request.username,
                Users.phone_number == create_user_request.phone_number,
            )
        )
        .first()
    )

    if existing_user:
        if existing_user.email == create_user_request.email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        if existing_user.username == create_user_request.username:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
        if existing_user.phone_number == create_user_request.phone_number:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already registered")

    create_user_model = Users(
        email=create_user_request.email,  # Example email generation
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password= bcrypt_context.hash(create_user_request.password),  # In a real application, hash the password
        role=create_user_request.role,
        phone_number=create_user_request.phone_number,  # Default to None, can be updated later
        is_active=True  # Default to active user
    )
    db.add(create_user_model)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")


@router.post('/token', response_model=Token, status_code=status.HTTP_200_OK)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")      
    
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))  # Replace user_id with actual user ID
    return {"access_token": token, "token_type": "bearer"}

