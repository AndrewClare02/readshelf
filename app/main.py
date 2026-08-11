from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db
from app.routes import bookmarks, tags


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="readshelf", lifespan=lifespan)

app.include_router(bookmarks.router)
app.include_router(tags.router)


@app.get("/health")
def health():
    return {"status": "ok"}
