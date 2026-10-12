import time
from dataclasses import dataclass

import requests
from fastapi import HTTPException, Request
from jose import JWTError, jwt

from app.core.config import settings

JWKS_URL = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
JWKS_CACHE_TTL_SECONDS = 3600

_jwks_cache: dict = {"keys": [], "fetched_at": 0.0}


@dataclass
class CurrentUser:
    id: str
    email: str | None


def _fetch_jwks() -> list[dict]:
    response = requests.get(JWKS_URL, timeout=5)
    response.raise_for_status()
    return response.json().get("keys", [])


def _get_jwk_for_kid(kid: str, force_refresh: bool = False) -> dict | None:
    cache_is_stale = time.time() - _jwks_cache["fetched_at"] > JWKS_CACHE_TTL_SECONDS

    if force_refresh or cache_is_stale or not _jwks_cache["keys"]:
        _jwks_cache["keys"] = _fetch_jwks()
        _jwks_cache["fetched_at"] = time.time()

    for key in _jwks_cache["keys"]:
        if key.get("kid") == kid:
            return key

    return None


def _decode_token(token: str) -> dict:
    header = jwt.get_unverified_header(token)
    alg = header.get("alg")

    # Older Supabase projects sign with a shared HS256 secret. Newer projects
    # use asymmetric keys (ES256/RS256) published via a JWKS endpoint.
    if alg == "HS256":
        return jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )

    kid = header.get("kid")
    jwk = _get_jwk_for_kid(kid) if kid else None

    if jwk is None:
        # Key rotation may have happened since we last cached the JWKS.
        jwk = _get_jwk_for_kid(kid, force_refresh=True) if kid else None

    if jwk is None:
        raise JWTError(f"No matching JWKS key found for kid={kid}")

    return jwt.decode(
        token,
        jwk,
        algorithms=[alg],
        audience="authenticated",
    )


def get_current_user(request: Request) -> CurrentUser:
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header",
        )

    token = auth_header.removeprefix("Bearer ").strip()

    try:
        payload = _decode_token(token)
    except JWTError as exc:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid or expired token: {exc}",
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Could not verify token against Supabase: {exc}",
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Token missing subject claim",
        )

    return CurrentUser(id=user_id, email=payload.get("email"))
