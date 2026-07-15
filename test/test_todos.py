
from ..routers.todos import get_db, get_current_user
from fastapi import status
from .utils import *
from ..models import Todo
from ..main import app




app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user



def test_read_all_authenticated(test_todo):
    response = client.get("/todos/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"title": "Test Todo", "description": "This is a test todo", "priority": 3, "completed": False, "owner_id": 1, "id": 1}]

def test_one_todo_authenticated(test_todo):
    response = client.get("/todos/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"title": "Test Todo",
                               "description": "This is a test todo", 
                               "priority": 3, "completed": False, 
                               "owner_id": 1, "id": 1}

def test_one_authenticated_not_found():
    response = client.get("/todos/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo with id 999 not found"}

def test_create_todo(test_todo):
    new_todo = {
        "title": "New Todo",
        "description": "This is a new todo",
        "priority": 2,
        "completed": False
    }
    response = client.post("/todos/todo", json=new_todo)
    assert response.status_code == status.HTTP_201_CREATED
    db = TestingSessionLocal()
    created_todo = db.query(Todo).filter(Todo.id == 2).first()
    assert created_todo.description == new_todo.get("description")
    assert created_todo.title == new_todo.get("title")
    assert created_todo.priority == new_todo.get("priority")
    assert created_todo.completed == new_todo.get("completed")

def test_update_todo(test_todo):
    updated_todo = {
        "title": "Updated Todo",
        "description": "This is an updated todo",
        "priority": 5,
        "completed": False
    }
    response = client.put("/todos/todo/1", json=updated_todo)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    updated_todo_db = db.query(Todo).filter(Todo.id == 1).first()
    assert updated_todo_db.title == updated_todo.get("title")
    assert updated_todo_db.description == updated_todo.get("description")
    assert updated_todo_db.priority == updated_todo.get("priority")
    assert updated_todo_db.completed == updated_todo.get("completed")

def test_update_todo_not_found(test_todo):
    updated_todo = {
        "title": "Updated Todo",
        "description": "This is an updated todo",
        "priority": 5,
        "completed": False
    }
    response = client.put("/todos/todo/999", json=updated_todo)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo with id 999 not found"}

def test_delete_todo(test_todo):
    response = client.delete("/todos/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    deleted_todo = db.query(Todo).filter(Todo.id == 1).first()
    assert deleted_todo is None

def test_delete_todo_not_found():
    response = client.delete("/todos/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo with id 999 not found"}