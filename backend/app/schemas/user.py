from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.user import UserRole


class UserCreate(BaseModel):
    """POST /api/auth/users request body (admin only)."""
    username: str
    password: str
    role: UserRole


class UserResponse(BaseModel):
    """Response body for user endpoints — no password field."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: UserRole
    created_at: datetime
