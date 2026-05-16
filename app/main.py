from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import joinedload, Session
import os

from app.db import init_db, create_default_data, get_db, User, ToDo, Category
from app.schemas import TodoCreate, TodoRead, TodoUpdate, CategoryRead

app = FastAPI(title="ToDo API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


def get_current_user(api_key: str = Depends(api_key_header), db: Session = Depends(get_db)) -> User:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )

    user = db.execute(select(User).where(User.api_key == api_key)).scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return user


@app.on_event("startup")
def startup_event():
    init_db()
    create_default_data()


@app.get("/", summary="Serve main page")
def root():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"message": "ToDo API is running"}


@app.get("/categories", response_model=list[CategoryRead])
def list_categories(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    categories = db.execute(select(Category).order_by(Category.name)).scalars().all()
    return categories


@app.get("/todos", response_model=list[TodoRead])
def list_todos(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    todos = (
        db.execute(
            select(ToDo)
            .options(joinedload(ToDo.category))
            .where(ToDo.user_id == current_user.id)
            .order_by(ToDo.created_at.desc())
        )
        .scalars()
        .all()
    )
    return todos


@app.post("/todos", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(todo_in: TodoCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    category = db.execute(select(Category).where(Category.id == todo_in.category_id)).scalars().first()
    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")

    todo = ToDo(
        user_id=current_user.id,
        category_id=category.id,
        text=todo_in.text,
        done=False,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@app.put("/todos/{todo_id}", response_model=TodoRead)
def update_todo(todo_id: int, todo_in: TodoUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    todo = db.execute(select(ToDo).where(ToDo.id == todo_id, ToDo.user_id == current_user.id)).scalars().first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ToDo not found")

    if todo_in.text is not None:
        todo.text = todo_in.text
    if todo_in.done is not None:
        todo.done = todo_in.done
    if todo_in.category_id is not None:
        category = db.execute(select(Category).where(Category.id == todo_in.category_id)).scalars().first()
        if not category:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")
        todo.category_id = category.id

    db.commit()
    db.refresh(todo)
    return todo


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    todo = db.execute(select(ToDo).where(ToDo.id == todo_id, ToDo.user_id == current_user.id)).scalars().first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ToDo not found")
    db.delete(todo)
    db.commit()
    return None

