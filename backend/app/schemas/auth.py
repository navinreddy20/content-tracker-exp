from pydantic import BaseModel


class Token(BaseModel):
    """Response body for POST /api/auth/login."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded JWT payload fields used internally by dependencies."""
    username: str
    role: str
