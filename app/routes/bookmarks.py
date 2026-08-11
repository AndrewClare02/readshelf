from fastapi import APIRouter, Depends

from app.auth import require_api_key

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"], dependencies=[Depends(require_api_key)])


@router.post("")
def create_bookmark():
    raise NotImplementedError


@router.get("")
def list_bookmarks(tag: str | None = None, q: str | None = None):
    raise NotImplementedError


@router.get("/{bookmark_id}")
def get_bookmark(bookmark_id: int):
    raise NotImplementedError


@router.patch("/{bookmark_id}")
def update_bookmark(bookmark_id: int):
    raise NotImplementedError


@router.delete("/{bookmark_id}")
def delete_bookmark(bookmark_id: int):
    raise NotImplementedError
