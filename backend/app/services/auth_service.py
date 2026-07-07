import logging
from typing import Dict, Optional

from fastapi import HTTPException, status
from jose import JWTError

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)

logger = logging.getLogger(__name__)


class AuthService:
    """Service layer implementing authentication business logic and token versioning."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, request: RegisterRequest) -> User:
        """Register a new user and create default settings."""
        existing_user = await self.user_repo.get_by_email(request.email)
        if existing_user:
            logger.warning(
                f"Registration failed: Email {request.email} already exists."
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        hashed_pw = hash_password(request.password)
        user = await self.user_repo.create(
            email=request.email,
            hashed_password=hashed_pw,
            full_name=request.full_name,
        )
        logger.info(f"Registered new user: {user.email} (ID: {user.id})")
        return user

    async def login(self, request: LoginRequest) -> TokenResponse:
        """Authenticate user credentials and issue versioned JWT tokens."""
        user = await self.user_repo.get_by_email(request.email)
        if not user or not verify_password(request.password, user.hashed_password):
            logger.warning(f"Login failed for email: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is inactive",
            )

        access_token = create_access_token(user.id, user.token_version)
        refresh_token = create_refresh_token(user.id, user.token_version)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh_token(self, refresh_token_str: str) -> TokenResponse:
        """Validate refresh token and embedded token_version, issuing new tokens."""
        try:
            payload = decode_token(refresh_token_str)
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type provided",
                )
            user_id: Optional[str] = payload.get("sub")
            token_version: Optional[int] = payload.get("token_version")
            if user_id is None or token_version is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                )
        except (JWTError, ValueError, KeyError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        if user.token_version != token_version:
            logger.warning(
                f"Token version mismatch for user {user.id}: DB={user.token_version}, Token={token_version}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session invalidated. Please log in again.",
            )

        # Issue rotated access and refresh tokens
        new_access_token = create_access_token(user.id, user.token_version)
        new_refresh_token = create_refresh_token(user.id, user.token_version)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def change_password(
        self, user: User, request: ChangePasswordRequest
    ) -> Dict[str, str]:
        """Change user password and increment token_version to invalidate all sessions."""
        if not verify_password(request.old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect old password",
            )

        new_hashed_pw = hash_password(request.new_password)
        new_version = await self.user_repo.update_password(user, new_hashed_pw)
        logger.info(
            f"Password changed for user {user.id}. Token version bumped to {new_version}."
        )

        return {
            "status": "success",
            "message": "Password changed successfully. All previous sessions invalidated.",
        }
