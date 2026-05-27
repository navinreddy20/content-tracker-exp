"""JWT encode / decode using python-jose.

Constants are read from app.core.config so they are configurable via .env.
Raises 401 HTTPException for any invalid or expired token.
"""
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.core.config import settings
from app.schemas.auth import TokenData


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Encode *data* into a signed JWT; default expiry is 60 minutes."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=60))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> TokenData:
    """Decode and validate *token*; return TokenData on success.

    Raises HTTP 401 if the token is missing required fields, expired, or
    its signature does not verify.
    """
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        raise credentials_exc

    username: str | None = payload.get("sub")
    role: str | None = payload.get("role")
    if username is None or role is None:
        raise credentials_exc

    return TokenData(username=username, role=role)
