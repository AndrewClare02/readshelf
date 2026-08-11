from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session, select

from app.auth import require_api_key
from app.db import get_session
from app.enrichment import fetch_and_store_title
from app.models import Bookmark, Tag
from app.schemas import BookmarkCreate, BookmarkRead, BookmarkUpdate

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"], dependencies=[Depends(require_api_key)])


def _to_read(bookmark: Bookmark) -> BookmarkRead:
    return BookmarkRead(
        id=bookmark.id,
        url=bookmark.url,
        title=bookmark.title,
        created_at=bookmark.created_at,
        tags=[tag.name for tag in bookmark.tags],
    )


def _get_or_create_tags(session: Session, names: list[str]) -> list[Tag]:
    tags = []
    for name in names:
        tag = session.exec(select(Tag).where(Tag.name == name)).first()
        if tag is None:
            tag = Tag(name=name)
            session.add(tag)
            session.flush()
        tags.append(tag)
    return tags


def _get_bookmark_or_404(session: Session, bookmark_id: int) -> Bookmark:
    bookmark = session.get(Bookmark, bookmark_id)
    if bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return bookmark


@router.post("", response_model=BookmarkRead, status_code=201)
def create_bookmark(
    payload: BookmarkCreate, background_tasks: BackgroundTasks, session: Session = Depends(get_session)
):
    bookmark = Bookmark(url=payload.url, tags=_get_or_create_tags(session, payload.tags))
    session.add(bookmark)
    session.commit()
    session.refresh(bookmark)
    background_tasks.add_task(fetch_and_store_title, bookmark.id, bookmark.url)
    return _to_read(bookmark)


@router.get("", response_model=list[BookmarkRead])
def list_bookmarks(tag: str | None = None, q: str | None = None, session: Session = Depends(get_session)):
    statement = select(Bookmark)
    if tag is not None:
        statement = statement.join(Bookmark.tags).where(Tag.name == tag)
    if q is not None:
        like = f"%{q}%"
        statement = statement.where((Bookmark.title.ilike(like)) | (Bookmark.url.ilike(like)))
    bookmarks = session.exec(statement).all()
    return [_to_read(b) for b in bookmarks]


@router.get("/{bookmark_id}", response_model=BookmarkRead)
def get_bookmark(bookmark_id: int, session: Session = Depends(get_session)):
    return _to_read(_get_bookmark_or_404(session, bookmark_id))


@router.patch("/{bookmark_id}", response_model=BookmarkRead)
def update_bookmark(bookmark_id: int, payload: BookmarkUpdate, session: Session = Depends(get_session)):
    bookmark = _get_bookmark_or_404(session, bookmark_id)
    if payload.title is not None:
        bookmark.title = payload.title
    if payload.tags is not None:
        bookmark.tags = _get_or_create_tags(session, payload.tags)
    session.add(bookmark)
    session.commit()
    session.refresh(bookmark)
    return _to_read(bookmark)


@router.delete("/{bookmark_id}", status_code=204)
def delete_bookmark(bookmark_id: int, session: Session = Depends(get_session)):
    bookmark = _get_bookmark_or_404(session, bookmark_id)
    session.delete(bookmark)
    session.commit()
