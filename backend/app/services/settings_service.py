import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.user_settings import UserSettings
from app.schemas.settings import SettingsResponse

logger = logging.getLogger(__name__)

KNOWN_AGENTS = {"logical", "rational", "practical", "spiritual", "skeptical"}


class SettingsService:
    """Service layer for managing user profile and preferences."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_settings(self, user: User) -> SettingsResponse:
        """Get current user profile and preferences, initializing default settings if missing."""
        if not user.settings:
            logger.info(
                f"UserSettings missing for user {user.id}; initializing defaults."
            )
            settings_obj = UserSettings(user_id=user.id)
            self.db.add(settings_obj)
            await self.db.commit()
            await self.db.refresh(user)

        return SettingsResponse.model_validate(
            {
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "agent_weights": user.settings.agent_weights,
                "preferred_model_settings": user.settings.preferred_model_settings,
            }
        )

    async def update_agent_weights(
        self, user: User, weights: Dict[str, Any]
    ) -> SettingsResponse:
        """Validate and update per-agent weights for the Council Aggregator."""
        if set(weights.keys()) != KNOWN_AGENTS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agent weights must contain exactly: logical, rational, practical, spiritual, skeptical",
            )

        total_weight = 0.0
        for key, val in weights.items():
            if not isinstance(val, (int, float)) or val < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Weight for '{key}' must be a finite, non-negative number.",
                )
            total_weight += float(val)

        if total_weight <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one agent weight must be greater than 0.",
            )

        if not user.settings:
            user.settings = UserSettings(user_id=user.id)
            self.db.add(user.settings)

        # Force SQLAlchemy to detect JSON mutation by assigning a new dictionary
        user.settings.agent_weights = dict(weights)
        await self.db.commit()
        await self.db.refresh(user)
        logger.info(f"Updated agent weights for user {user.id}: {weights}")

        return await self.get_settings(user)

    async def update_profile(
        self, user: User, full_name: Optional[str]
    ) -> SettingsResponse:
        """Update user display name."""
        user.full_name = full_name
        await self.db.commit()
        await self.db.refresh(user)
        logger.info(f"Updated profile display name for user {user.id}")

        return await self.get_settings(user)
