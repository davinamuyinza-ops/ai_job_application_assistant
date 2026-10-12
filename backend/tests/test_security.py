import time

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from app.core.config import settings
from app.core.security import CurrentUser, get_current_user
from tests.conftest import make_token


@pytest.fixture
def secured_client():
    """A tiny app protected by the real get_current_user (no overrides)."""
    app = FastAPI()

    @app.get("/whoami")
    def whoami(user: CurrentUser = Depends(get_current_user)):
        return {"id": user.id, "email": user.email}

    return TestClient(app)


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def test_valid_token_identifies_the_user(secured_client):
    token = make_token(sub="user-42", email="jo@example.com")

    response = secured_client.get("/whoami", headers=bearer(token))

    assert response.json() == {"id": "user-42", "email": "jo@example.com"}


def test_missing_authorization_header_is_rejected(secured_client):
    assert secured_client.get("/whoami").status_code == 401


def test_non_bearer_authorization_is_rejected(secured_client):
    assert secured_client.get("/whoami", headers={"Authorization": "Basic abc"}).status_code == 401


def test_garbage_token_is_rejected(secured_client):
    assert secured_client.get("/whoami", headers=bearer("garbage")).status_code == 401


def test_expired_token_is_rejected(secured_client):
    assert secured_client.get("/whoami", headers=bearer(make_token(exp=1))).status_code == 401


def test_wrong_audience_is_rejected(secured_client):
    assert secured_client.get("/whoami", headers=bearer(make_token(aud="other"))).status_code == 401


def test_token_signed_with_another_secret_is_rejected(secured_client):
    forged = jwt.encode(
        {"sub": "attacker", "aud": "authenticated", "exp": int(time.time()) + 600},
        "not-the-real-secret",
        algorithm="HS256",
    )

    assert secured_client.get("/whoami", headers=bearer(forged)).status_code == 401


def test_token_without_subject_is_rejected(secured_client):
    token = jwt.encode(
        {"aud": "authenticated", "exp": int(time.time()) + 600},
        settings.supabase_jwt_secret,
        algorithm="HS256",
    )

    assert secured_client.get("/whoami", headers=bearer(token)).status_code == 401
