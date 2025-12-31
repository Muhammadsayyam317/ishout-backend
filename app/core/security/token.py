import jwt
from typing import Dict, Any
from app.config import config
from fastapi import HTTPException

from app.core.exception import UnauthorizedException


def verify_token(token: str) -> Dict[str, Any]:
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    if not config.JWT_SECRET_KEY:
        raise HTTPException(status_code=500, detail="JWT secret not configured")
    try:
        payload = jwt.decode(
            token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM]
        )
        return payload or {}
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException(message="Token has expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedException(message="Invalid token")


def get_current_user_from_token(token: str) -> Dict[str, Any]:
    payload = verify_token(token)
    return {
        "user_id": payload.get("user_id"),
        "email": payload.get("email"),
        "role": payload.get("role"),
    }
