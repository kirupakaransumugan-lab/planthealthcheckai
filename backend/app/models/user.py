from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import utc_now

if TYPE_CHECKING:
    from app.models.person import Person
    from app.models.plant import Plant


class User(Base):
    """Table `users`: one row per registered account."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(150))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    people: Mapped[list["Person"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    plants: Mapped[list["Plant"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
