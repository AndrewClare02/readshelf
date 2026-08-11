from fastapi import APIRouter, Depends

from app.auth import require_api_key

router = APIRouter(prefix="/tags", tags=["tags"], dependencies=[Depends(require_api_key)])


@router.get("")
def list_tags():
    raise NotImplementedError
