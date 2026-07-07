from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.settings import (
    AgentWeightsUpdate,
    ProfileUpdate,
    SettingsResponse,
)
from app.services.settings_service import SettingsService

router = APIRouter()


def get_settings_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SettingsService:
    """Dependency injection for SettingsService."""
    return SettingsService(db)


@router.get(
    "",
    response_model=SettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user profile and settings",
)
async def get_settings(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[SettingsService, Depends(get_settings_service)],
):
    """Return the profile and preferences of the authenticated user."""
    return await service.get_settings(current_user)


@router.patch(
    "/agent-weights",
    response_model=SettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Update per-agent weights",
)
async def update_agent_weights(
    request: AgentWeightsUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[SettingsService, Depends(get_settings_service)],
):
    """Update per-agent weights for the Council Aggregator."""
    return await service.update_agent_weights(current_user, request.agent_weights)


@router.patch(
    "/profile",
    response_model=SettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user profile display name",
)
async def update_profile(
    request: ProfileUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[SettingsService, Depends(get_settings_service)],
):
    """Update user display name."""
    return await service.update_profile(current_user, request.full_name)
