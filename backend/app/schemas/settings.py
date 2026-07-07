import uuid
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class AgentWeightsUpdate(BaseModel):
    """Schema for updating per-agent weights in the Aggregator."""

    agent_weights: Dict[str, Any]


class ProfileUpdate(BaseModel):
    """Schema for updating user profile display name."""

    full_name: Optional[str] = None


class SettingsResponse(BaseModel):
    """Response schema combining user profile and their preferences."""

    user_id: uuid.UUID
    email: str
    full_name: Optional[str] = None
    agent_weights: Dict[str, Any]
    preferred_model_settings: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)
