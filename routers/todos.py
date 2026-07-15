from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Path, APIRouter, Request
from pydantic import BaseModel, Field
from ..database import SessionLocal
from sqlalchemy.orm import Session
from starlette import status
from ..models import Todo
from .auth import get_current_user
from starlette.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="TodoApp/templates")

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=300)
    priority: int = Field(ge=1, le=5)
    completed: bool

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")  # Clear the access token cookie
    return redirect_response

## Pages ##
@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        todos = db.query(Todo).filter(Todo.owner_id == user.get("id")).all()
        return templates.TemplateResponse(request, "todo.html", {"request": request, "todos": todos, "user": user})
    except Exception as e:
        return redirect_to_login()

@router.get("/add-todo-page")
async def render_add_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        return templates.TemplateResponse(request, "add-todo.html", {"request": request, "user": user})
    except Exception as e:
        return redirect_to_login()

@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        todo = db.query(Todo).filter(Todo.id == todo_id).first()
        return templates.TemplateResponse(request, "edit-todo.html", {"request": request, "todo": todo, "user": user})
    except Exception as e:
        return redirect_to_login()


    

## Endpoints ##

@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):    
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    return db.query(Todo).filter(Todo.owner_id == user.get("id")).all()  # Filter todos by the authenticated user's ID

@router.get('/todo/{todo_id}', status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    todo_model = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get("id")).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")

@router.post('/todo', status_code=status.HTTP_201_CREATED)
async def create_todo(usertodo: TodoRequest, db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    todo_model = Todo(**usertodo.dict(), owner_id=user.get("id"))  # Set the owner_id to the authenticated user's ID
    db.add(todo_model)
    db.commit()

@router.put('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo( todo: TodoRequest, user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    todo_model = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.completed = todo.completed
    db.add(todo_model)
    db.commit()

@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    todo_model = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    db.query(Todo).filter(Todo.id == todo_id).delete()
    db.commit()