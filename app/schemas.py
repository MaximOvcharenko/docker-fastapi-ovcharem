from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CategoryRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class TodoCreate(BaseModel):
    text: str
    category_id: int


class TodoUpdate(BaseModel):
    text: Optional[str] = None
    done: Optional[bool] = None
    category_id: Optional[int] = None


class TodoRead(BaseModel):
    id: int
    text: str
    done: bool
    created_at: datetime
    category: Optional[CategoryRead] = None

    class Config:
        from_attributes = True
