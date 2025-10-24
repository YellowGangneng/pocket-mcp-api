"""SQLAlchemy model for likes."""

from sqlalchemy import Enum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from pocket.app.core.database import Base
from pocket.app.models.enums import TargetEnum


class Like(Base):
    """Represents a user's expressed preference for an entity."""

    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint("target_id", "target_type", "user_id", name="uq_likes_target_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    target_id: Mapped[int] = mapped_column(Integer, nullable=False)
    target_type: Mapped[TargetEnum] = mapped_column(Enum(TargetEnum, name="target"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
