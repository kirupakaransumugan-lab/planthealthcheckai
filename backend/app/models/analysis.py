from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import utc_now

if TYPE_CHECKING:
    from app.models.person import Person
    from app.models.plant import Plant


class Analysis(Base):
    """Table `analyses`: one AI check of one plant. This table is the history."""

    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id", ondelete="CASCADE"), index=True)

    symptom_text: Mapped[str | None] = mapped_column(Text)
    has_photo: Mapped[bool] = mapped_column(Boolean, default=False)
    model_used: Mapped[str] = mapped_column(String(100))

    visible_signs: Mapped[str | None] = mapped_column(Text)
    explanation: Mapped[str] = mapped_column(Text)
    expert_advice: Mapped[str] = mapped_column(Text)
    confidence_note: Mapped[str] = mapped_column(Text)
    raw_response: Mapped[str] = mapped_column(Text)   # full AI JSON, kept for re-processing

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, index=True)

    plant: Mapped["Plant"] = relationship(back_populates="analyses")
    person: Mapped["Person"] = relationship(back_populates="analyses")
    issues: Mapped[list["AnalysisIssue"]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
        order_by="AnalysisIssue.position"
    )
    suggestions: Mapped[list["AnalysisSuggestion"]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
        order_by="AnalysisSuggestion.position"
    )


class AnalysisIssue(Base):
    """Table `analysis_issues`: one possible issue named in an analysis."""

    __tablename__ = "analysis_issues"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), index=True
    )
    issue_name: Mapped[str] = mapped_column(String(255))
    position: Mapped[int] = mapped_column(Integer)

    analysis: Mapped["Analysis"] = relationship(back_populates="issues")


class AnalysisSuggestion(Base):
    """Table `analysis_suggestions`: one care suggestion (three per analysis)."""

    __tablename__ = "analysis_suggestions"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), index=True
    )
    suggestion: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer)

    analysis: Mapped["Analysis"] = relationship(back_populates="suggestions")
