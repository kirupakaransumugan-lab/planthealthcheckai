from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import utc_now

if TYPE_CHECKING:
    from app.models.analysis import Analysis
    from app.models.person import Person
    from app.models.user import User


class Plant(Base):
    """Table `plants`: a plant that belongs to a user."""

    __tablename__ = "plants"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    plant_type: Mapped[str] = mapped_column(String(100))
    location: Mapped[str | None] = mapped_column(String(150))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    user: Mapped["User"] = relationship(back_populates="plants")
    person: Mapped["Person"] = relationship(back_populates="plants")
    analyses: Mapped[list["Analysis"]] = relationship(
        back_populates="plant", cascade="all, delete-orphan"
    )
