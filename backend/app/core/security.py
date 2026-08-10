from dataclasses import dataclass

from fastapi import HTTPException, Request
from jose import JWTError, jwt

from app.core.config import settings


@dataclass
class CurrentUser:
    id: str
    email: str | None


def get_current_user(request: Request) -> CurrentUser:
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header",
        )

    token = auth_header.removeprefix("Bearer ").strip()

    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid or expired token: {exc}",
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Token missing subject claim",
        )

    return CurrentUser(id=user_id, email=payload.get("email"))
