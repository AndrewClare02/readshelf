from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class BookmarkTagLink(SQLModel, table=True):
    bookmark_id: Optional[int] = Field(default=None, foreign_key="bookmark.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    bookmarks: list["Bookmark"] = Relationship(back_populates="tags", link_model=BookmarkTagLink)


class Bookmark(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    title: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    tags: list[Tag] = Relationship(back_populates="bookmarks", link_model=BookmarkTagLink)
