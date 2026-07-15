from sqlalchemy import StaticPool, create_engine, text
from sqlalchemy.orm import sessionmaker
from ..database import Base
from fastapi.testclient import TestClient
from ..main import app
import pytest
from ..models import Todo, Users
from ..routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, 
                       connect_args={"check_same_thread": False},
                       poolclass=StaticPool)  # Use StaticPool for SQLite in-memory database

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {"id": 1, "username": "shreecoding", "user_role": "admin"}

client = TestClient(app)

@pytest.fixture
def test_todo():
    todo = Todo(title="Test Todo", description="This is a test todo", priority=3, completed=False, owner_id=1)
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()


@pytest.fixture
def test_user():
    hashed_password = bcrypt_context.hash("test1234!")
    user = Users(username="shreecoding", 
                 email="shrimandhar@email.com",
                 first_name="Shrimandhar",
                 last_name="Magdum",
                 hashed_password=hashed_password, 
                 role="admin",
                 phone_number="751731008")
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()