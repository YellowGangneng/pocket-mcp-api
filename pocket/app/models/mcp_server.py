"""SQLAlchemy model for MCP servers."""

from datetime import datetime

from sqlalchemy import ARRAY, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from pocket.app.core.database import Base
from pocket.app.models.enums import IOEnum, StatusEnum, VisibilityEnum


class MCPServer(Base):
    """Represents an MCP server definition uploaded by a user."""

    __tablename__ = "mcp_servers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[StatusEnum | None] = mapped_column(Enum(StatusEnum, name="status"), nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    io_type: Mapped[IOEnum | None] = mapped_column(Enum(IOEnum, name="io"), nullable=True)
    usage_count: Mapped[int | None] = mapped_column(Integer, default=0)
    visibility_scope: Mapped[VisibilityEnum | None] = mapped_column(
        Enum(VisibilityEnum, name="visibility"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.now()
    )
    company_code: Mapped[int | None] = mapped_column(Integer)

