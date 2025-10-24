"""SQLAlchemy model for application users."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from pocket.app.core.database import Base
from pocket.app.models.enums import RoleEnum, StatusEnum


class User(Base):
    """Represents a registered user account."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    user_name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[RoleEnum | None] = mapped_column(Enum(RoleEnum, name="role"), nullable=True)
    status: Mapped[StatusEnum | None] = mapped_column(Enum(StatusEnum, name="status"), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.now()
    )
    company_code: Mapped[int | None] = mapped_column(Integer)
