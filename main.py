from pathlib import Path

from fastapi import FastAPI, Request, status
try:
    from .routers import auth, todos, admin, users
    from . import models
    from . import database
except ImportError:
    from routers import auth, todos, admin, users
    import models
    import database
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse


app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

models.Base.metadata.create_all(bind=database.engine)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.get("/")
def test(request: Request):
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)

@app.get("/healthy")
def read_health():
    return {"status": "healthy"}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
