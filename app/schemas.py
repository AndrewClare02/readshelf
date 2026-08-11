from datetime import datetime

from pydantic import BaseModel


class BookmarkCreate(BaseModel):
    url: str
    tags: list[str] = []


class BookmarkUpdate(BaseModel):
    title: str | None = None
    tags: list[str] | None = None


class BookmarkRead(BaseModel):
    id: int
    url: str
    title: str | None
    created_at: datetime
    tags: list[str]


class TagRead(BaseModel):
    id: int
    name: str
