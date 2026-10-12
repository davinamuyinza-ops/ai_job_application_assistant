import os

# Tests never touch the real database, keys, or .env. Environment variables
# beat the .env file in pydantic-settings, so set dummies before importing.
os.environ["OPENAI_API_KEY"] = "test-key-not-real"
os.environ["ADZUNA_APP_ID"] = "test-adzuna-id"
os.environ["ADZUNA_APP_KEY"] = "test-adzuna-key"
os.environ["DATABASE_URL"] = "postgresql://nobody:nothing@localhost:1/none"
os.environ["SUPABASE_URL"] = "https://test-project.supabase.co"
os.environ["SUPABASE_JWT_SECRET"] = "test-jwt-secret-for-unit-tests-only-0123456789"

import time  # noqa: E402

import pytest  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from jose import jwt  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.dialects.postgresql import JSONB  # noqa: E402
from sqlalchemy.ext.compiler import compiles  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.database import Base, get_db  # noqa: E402
from app.core.security import CurrentUser, get_current_user  # noqa: E402
from app.models import application, master_resume  # noqa: E402,F401
from app.routers import applications as applications_router  # noqa: E402
from app.routers import resume as resume_router  # noqa: E402


# The real database is Postgres (JSONB); tests use in-memory SQLite, which
# can store the same data as plain JSON.
@compiles(JSONB, "sqlite")
def _jsonb_as_json_on_sqlite(type_, compiler, **kwargs):
    return "JSON"


def make_token(**overrides) -> str:
    claims = {"sub": "user-a", "aud": "authenticated", "exp": int(time.time()) + 600}
    claims.update(overrides)
    return jwt.encode(claims, settings.supabase_jwt_secret, algorithm="HS256")


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False)()
    yield session
    session.close()


class Acting:
    """Lets a test switch which user the app believes is signed in."""

    def __init__(self):
        self.user_id = "user-a"


@pytest.fixture
def acting():
    return Acting()


@pytest.fixture
def client(db_session, acting):
    """The real routers on a throwaway app, a throwaway database, and a
    switchable signed-in user (so ownership rules can be tested)."""
    app = FastAPI()
    app.include_router(applications_router.router)
    app.include_router(resume_router.router)

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id=acting.user_id, email=None
    )

    return TestClient(app)


def application_body(**overrides):
    body = {
        "company": "Acme",
        "role": "Developer",
        "match_score": 80,
        "priority": "High",
        "should_apply": "True",
        "status": "Saved",
        "application_date": "1/1/2026",
        "job_link": "https://example.com/job",
        "job_analysis": {"k": 1},
    }
    body.update(overrides)
    return body
