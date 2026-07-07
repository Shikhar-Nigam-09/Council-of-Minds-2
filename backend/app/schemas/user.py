import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserSettingsResponse(BaseModel):
    """Schema for returning user settings."""

    id: uuid.UUID
    user_id: uuid.UUID
    agent_weights: Dict[str, Any]
    preferred_model_settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    """Schema for returning user profile data."""

    id: uuid.UUID
    email: EmailStr
    full_name: Optional[str] = None
    token_version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    settings: Optional[UserSettingsResponse] = None

    model_config = ConfigDict(from_attributes=True)
