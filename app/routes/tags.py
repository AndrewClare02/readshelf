from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.auth import require_api_key
from app.db import get_session
from app.models import Tag
from app.schemas import TagRead

router = APIRouter(prefix="/tags", tags=["tags"], dependencies=[Depends(require_api_key)])


@router.get("", response_model=list[TagRead])
def list_tags(session: Session = Depends(get_session)):
    return session.exec(select(Tag)).all()
