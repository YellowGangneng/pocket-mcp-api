"""SQLAlchemy model for activity logs."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from pocket.app.core.database import Base
from pocket.app.models.enums import ActivityEnum, DeviceEnum, TargetEnum


class ActivityLog(Base):
    """Captures notable user activities for auditing."""

    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    activity_type: Mapped[ActivityEnum | None] = mapped_column(Enum(ActivityEnum, name="activity"), nullable=True)
    target_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_type: Mapped[TargetEnum | None] = mapped_column(Enum(TargetEnum, name="target"), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String, nullable=True)
    device: Mapped[DeviceEnum | None] = mapped_column(Enum(DeviceEnum, name="device"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.now()
    )
    company_code: Mapped[int | None] = mapped_column(Integer)

