import os
import secrets

from fastapi import Header, HTTPException, status


# Read at import time so a missing key fails app startup, not the first request.
API_KEY = os.environ["READSHELF_API_KEY"]


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if x_api_key is None or not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid X-API-Key header")
