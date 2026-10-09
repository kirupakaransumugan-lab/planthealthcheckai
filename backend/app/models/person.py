from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import utc_now

if TYPE_CHECKING:
    from app.models.analysis import Analysis
    from app.models.plant import Plant
    from app.models.user import User


class Person(Base):
    """Table `people`: someone the logged-in user checks plants for.

    One login account can manage many people. Plants and analyses belong to a
    person, so each person has their own history.
    """

    __tablename__ = "people"
    __table_args__ = (
        UniqueConstraint("owner_id", "name", name="uq_people_owner_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    location: Mapped[str | None] = mapped_column(String(150))
    notes: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    owner: Mapped["User"] = relationship(back_populates="people")
    plants: Mapped[list["Plant"]] = relationship(
        back_populates="person", cascade="all, delete-orphan"
    )
    analyses: Mapped[list["Analysis"]] = relationship(
        back_populates="person", cascade="all, delete-orphan"
    )
