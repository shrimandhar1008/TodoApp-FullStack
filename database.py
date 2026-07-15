from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Shri%400177@localhost/TodoApplicationDatabase"
# SQLALCHEMY_DATABASE_URL = "mysql://root:Shri%400177@localhost/TodoApplication"
SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}  # Only needed for SQLite
)
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL
# )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()