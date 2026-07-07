from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        description="Password must be at least 8 characters long",
    )
    full_name: Optional[str] = Field(default=None, max_length=255)


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response schema containing JWT access and refresh tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    """Request schema for refreshing access token."""

    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Request schema for changing user password."""

    old_password: str
    new_password: str = Field(
        ...,
        min_length=8,
        description="New password must be at least 8 characters long",
    )
