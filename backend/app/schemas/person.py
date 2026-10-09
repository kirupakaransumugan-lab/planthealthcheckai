from pydantic import BaseModel, Field, field_validator


# ---------- Requests ----------

class PersonCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    location: str | None = Field(default=None, max_length=150)
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Please enter a name.")

        return value

    @field_validator("location", "notes")
    @classmethod
    def blank_to_none(cls, value: str | None) -> str | None:
        value = value.strip() if value else None
        return value or None


class PersonUpdate(PersonCreate):
    """Same fields as PersonCreate; all of them are replaced."""


# ---------- Responses (the structured JSON the API returns) ----------

class PersonOut(BaseModel):
    id: int
    name: str
    location: str | None = None
    notes: str | None = None
    analysis_count: int = Field(description="How many saved checks this person has.")
    created_at: str = Field(description="UTC time, ISO 8601, ends with Z.")


class PeopleResponse(BaseModel):
    """What GET /api/people returns."""

    people: list[PersonOut]


class PersonResponse(BaseModel):
    person: PersonOut
