"""Pydantic schemas for MCP server resources."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from pocket.app.models.enums import DeviceEnum, IOEnum, StatusEnum, VisibilityEnum


class MCPServerBase(BaseModel):
    """Shared properties for MCP server payloads."""

    title: Optional[str] = Field(default=None, description="Display title for the MCP server.")
    description: str = Field(..., description="Detailed description of the MCP server.")
    status: Optional[StatusEnum] = Field(default=None, description="Lifecycle status of the server.")
    tags: Optional[List[str]] = Field(default=None, description="Optional list of descriptive tags.")
    io_type: Optional[IOEnum] = Field(default=None, description="Expected IO direction for the server.")
    visibility_scope: Optional[VisibilityEnum] = Field(
        default=None, description="Visibility scope controlling who can access the server."
    )
    company_code: Optional[int] = Field(default=None, description="Company identifier for multi-tenant support.")


class MCPServerCreate(MCPServerBase):
    """Payload for creating a new MCP server."""

    user_id: int = Field(default=1, description="Identifier of the user creating the server.")
    device: Optional[DeviceEnum] = Field(
        default=None,
        description="Client device type used for auditing when creating the server.",
    )


class MCPServerUpdate(BaseModel):
    """Payload for updating an existing MCP server."""

    title: Optional[str] = Field(default=None, description="Updated display title.")
    description: Optional[str] = Field(default=None, description="Updated description text.")
    status: Optional[StatusEnum] = Field(default=None, description="Updated lifecycle status.")
    tags: Optional[List[str]] = Field(default=None, description="Updated set of tags.")
    io_type: Optional[IOEnum] = Field(default=None, description="Updated IO direction.")
    visibility_scope: Optional[VisibilityEnum] = Field(default=None, description="Updated visibility scope.")
    company_code: Optional[int] = Field(default=None, description="Updated company code if necessary.")
    user_id: int = Field(..., description="Identifier of the user requesting the update.")
    device: Optional[DeviceEnum] = Field(
        default=None,
        description="Device type for auditing on update operations.",
    )


class MCPServerRead(MCPServerBase):
    """Resource representation returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Primary key of the MCP server.")
    user_id: Optional[int] = Field(default=None, description="Identifier of the owner user.")
    usage_count: Optional[int] = Field(default=None, description="Recorded usage counter.")
    created_at: datetime = Field(..., description="Timestamp when the record was created.")


class MCPServerListResponse(BaseModel):
    """Response wrapper for MCP server list endpoints."""

    data: List[MCPServerRead] = Field(..., description="Collection of MCP server resources.")


class MCPServerDetailResponse(BaseModel):
    """Response wrapper for MCP server detail endpoint."""

    data: MCPServerRead = Field(..., description="Payload containing the MCP server details.")


class MCPServerCreateResponse(BaseModel):
    """Response payload returned after creating an MCP server."""

    message: str = Field(..., description="Human-readable status message.")
    data: MCPServerRead = Field(..., description="Payload containing the MCP server details.")
