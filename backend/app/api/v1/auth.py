from typing import Annotated, Dict

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthService:
    """Dependency injection for AuthService."""
    return AuthService(UserRepository(db))


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
@limiter.limit(settings.RATE_LIMIT_AUTH_PER_MINUTE)
async def register(
    request: Request,
    payload: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Register a new user and initialize default agent weights and settings."""
    return await auth_service.register(payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate and receive JWT tokens",
)
@limiter.limit(settings.RATE_LIMIT_AUTH_PER_MINUTE)
async def login(
    request: Request,
    payload: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Login with email and password to receive access and refresh tokens embedding token_version."""
    return await auth_service.login(payload)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token using refresh token",
)
async def refresh(
    request: RefreshRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Validate refresh token and current token_version, returning a new token pair."""
    return await auth_service.refresh_token(request.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Return the profile and settings of the currently authenticated user."""
    return current_user


@router.post(
    "/change-password",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Change password and invalidate all previous sessions",
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Change user password, increment token_version, and immediately invalidate all previously issued tokens."""
    return await auth_service.change_password(current_user, request)
