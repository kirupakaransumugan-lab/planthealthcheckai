from pydantic import BaseModel, Field, field_validator


class PlantAnalysisRequest(BaseModel):
    person_id: int = Field(description="Who the plant check is for (from GET /api/people).")
    plant_name: str = Field(min_length=1, max_length=100)
    plant_type: str = Field(min_length=1, max_length=100)
    location: str | None = Field(default=None, max_length=150)
    symptom: str = Field(description="What is wrong with the plant (at least 5 characters).")

    @field_validator("symptom")
    @classmethod
    def check_symptom(cls, value: str) -> str:
        value = value.strip()

        if len(value) < 5:
            raise ValueError("Describe the symptoms (at least 5 characters).")

        return value


class PlantAnalysisResult(BaseModel):
    """The structured answer Gemini must return."""

    possible_issues: list[str] = Field(
        description="Possible causes, most likely first. Never stated as certain."
    )
    explanation: str = Field(
        description="Short, simple explanation for a home gardener or farmer."
    )
    care_suggestions: list[str] = Field(
        description="Exactly three simple, practical care suggestions."
    )
    expert_advice: str = Field(
        description="When expert agricultural advice may be needed."
    )
    confidence_note: str = Field(
        description="A note that this is not a guaranteed diagnosis."
    )


class PlantAnalysisResponse(BaseModel):
    """What POST /api/plant/analyze returns."""

    success: bool
    analysis: PlantAnalysisResult
    analysis_id: int | None = Field(
        default=None,
        description="Database id of the saved history entry (null if saving failed)."
    )
    saved: bool = Field(description="True when the analysis was stored in history.")


class HistoryItem(BaseModel):
    """One saved analysis in the user's history."""

    id: int
    created_at: str = Field(description="UTC time, ISO 8601, ends with Z.")
    person_id: int
    person_name: str
    plant_name: str
    plant_type: str
    location: str | None = None
    symptom: str | None = None
    model_used: str = Field(description="The Gemini model that produced the analysis.")
    analysis: PlantAnalysisResult


class HistoryResponse(BaseModel):
    """What GET /api/plant/history returns, newest first."""

    history: list[HistoryItem]


class SuccessResponse(BaseModel):
    success: bool
