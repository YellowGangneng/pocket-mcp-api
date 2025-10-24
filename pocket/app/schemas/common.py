"""Common reusable Pydantic schemas."""

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """Simple response containing only a message."""

    message: str = Field(..., description="Summary of the operation result.")
