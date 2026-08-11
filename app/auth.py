from fastapi import Header, HTTPException, status


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    # Stub for milestone 1: just requires the header to be present.
    # Milestone 2 will check it against READSHELF_API_KEY.
    if x_api_key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-API-Key header")
