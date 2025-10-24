"""Pydantic schemas for like resources."""

from typing import List

from pydantic import BaseModel, ConfigDict, Field

from pocket.app.models.enums import TargetEnum


class LikeBase(BaseModel):
    """Shared fields for like payloads."""

    target_id: int = Field(..., description="Identifier of the liked entity.")
    target_type: TargetEnum = Field(..., description="Type of the liked entity.")
    user_id: int = Field(..., description="Identifier of the user who liked the entity.")


class LikeCreate(LikeBase):
    """Payload for creating a like."""

    pass


class LikeRead(LikeBase):
    """Representation of a like entry."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Primary key of the like entry.")


class LikeListResponse(BaseModel):
    """List response for likes."""

    data: List[LikeRead] = Field(..., description="Collection of like entries.")


class MCPServerLikeRequest(BaseModel):
    """Payload for liking an MCP server."""

    user_id: int = Field(..., description="Identifier of the user performing the like action.")


class LikeActionResponse(BaseModel):
    """Standard response for like or unlike actions."""

    message: str = Field(..., description="Result message for the like action.")
