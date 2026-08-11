import os

os.environ.setdefault("READSHELF_API_KEY", "test-key")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.db as db_module
import app.enrichment as enrichment_module
from app.db import get_session
from app.main import app


@pytest.fixture(name="session")
def session_fixture(monkeypatch):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    monkeypatch.setattr(db_module, "engine", engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(autouse=True)
def no_real_fetch(monkeypatch):
    monkeypatch.setattr(enrichment_module, "_fetch_html", lambda url: None)


@pytest.fixture(name="client")
def client_fixture(session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="auth_headers")
def auth_headers_fixture():
    return {"X-API-Key": os.environ["READSHELF_API_KEY"]}
