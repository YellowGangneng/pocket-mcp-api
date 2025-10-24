"""Pydantic schemas for activity log resources."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from pocket.app.models.enums import ActivityEnum, DeviceEnum, TargetEnum


class ActivityLogBase(BaseModel):
    """Shared attributes for activity logs."""

    user_id: Optional[int] = Field(default=None, description="Identifier of the acting user.")
    activity_type: Optional[ActivityEnum] = Field(default=None, description="Type of activity performed.")
    target_id: Optional[int] = Field(default=None, description="Identifier of the activity target resource.")
    target_type: Optional[TargetEnum] = Field(default=None, description="Type of the activity target resource.")
    ip_address: Optional[str] = Field(default=None, description="Source IP address of the activity.")
    device: Optional[DeviceEnum] = Field(default=None, description="Device type used during the activity.")
    company_code: Optional[int] = Field(default=None, description="Company identifier for multi-tenancy.")


class ActivityLogCreate(ActivityLogBase):
    """Payload for creating a log entry manually."""

    activity_type: ActivityEnum = Field(..., description="Type of activity performed.")
    target_type: TargetEnum = Field(..., description="Type of target affected by the action.")


class ActivityLogUpdate(ActivityLogBase):
    """Payload for updating an existing log entry."""

    pass


class ActivityLogRead(ActivityLogBase):
    """Representation of an activity log entry."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Primary key of the log entry.")
    created_at: datetime = Field(..., description="Timestamp of when the log was recorded.")


class ActivityLogListResponse(BaseModel):
    """List response for activity logs."""

    data: List[ActivityLogRead] = Field(..., description="Collection of log entries.")


class ActivityLogResponse(BaseModel):
    """Response wrapper for single activity log operations."""

    message: str = Field(..., description="Human-readable status message.")
    data: ActivityLogRead = Field(..., description="Body containing the log entry.")
