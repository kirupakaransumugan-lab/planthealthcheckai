from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    Analysis,
    AnalysisIssue,
    AnalysisSuggestion,
    Person,
    Plant,
    User,
)
from app.schemas.plant import PlantAnalysisRequest, PlantAnalysisResult


def get_or_create_plant(
    db: Session, user: User, person: Person, name: str, plant_type: str, location: str | None
) -> Plant:
    # Checking the same plant again reuses its record, so its checks stay together
    plant = db.scalar(
        select(Plant).where(
            Plant.person_id == person.id,
            Plant.name == name,
            Plant.plant_type == plant_type
        )
    )

    if plant is None:
        plant = Plant(
            user_id=user.id,
            person_id=person.id,
            name=name,
            plant_type=plant_type,
            location=location
        )
        db.add(plant)
        db.flush()
    elif location:
        plant.location = location

    return plant


def save_analysis(
    db: Session,
    user: User,
    person: Person,
    request: PlantAnalysisRequest,
    result: PlantAnalysisResult,
    model_used: str
) -> Analysis:
    """Stores the plant and analysis under the chosen person in one transaction."""

    plant = get_or_create_plant(
        db, user, person, request.plant_name.strip(), request.plant_type.strip(), request.location
    )

    analysis = Analysis(
        plant_id=plant.id,
        user_id=user.id,
        person_id=person.id,
        symptom_text=request.symptom,
        model_used=model_used,
        explanation=result.explanation,
        expert_advice=result.expert_advice,
        confidence_note=result.confidence_note,
        raw_response=result.model_dump_json(),
        issues=[
            AnalysisIssue(issue_name=text[:255], position=i)
            for i, text in enumerate(result.possible_issues, start=1)
        ],
        suggestions=[
            AnalysisSuggestion(suggestion=text, position=i)
            for i, text in enumerate(result.care_suggestions[:3], start=1)
        ]
    )

    db.add(analysis)
    db.commit()

    return analysis


def _to_dict(analysis: Analysis) -> dict:
    return {
        "id": analysis.id,
        "created_at": analysis.created_at.isoformat() + "Z",   # stored as UTC
        "person_id": analysis.person_id,
        "person_name": analysis.person.name,
        "plant_name": analysis.plant.name,
        "plant_type": analysis.plant.plant_type,
        "location": analysis.plant.location,
        "symptom": analysis.symptom_text,
        "model_used": analysis.model_used,
        "analysis": {
            "possible_issues": [i.issue_name for i in analysis.issues],
            "explanation": analysis.explanation,
            "care_suggestions": [s.suggestion for s in analysis.suggestions],
            "expert_advice": analysis.expert_advice,
            "confidence_note": analysis.confidence_note
        }
    }


def list_history(db: Session, user: User, person_id: int | None = None) -> list[dict]:
    query = select(Analysis).where(Analysis.user_id == user.id)

    if person_id is not None:
        query = query.where(Analysis.person_id == person_id)

    rows = db.scalars(
        query
        .options(
            selectinload(Analysis.plant),
            selectinload(Analysis.person),
            selectinload(Analysis.issues),
            selectinload(Analysis.suggestions)
        )
        .order_by(Analysis.created_at.desc(), Analysis.id.desc())
    ).all()

    return [_to_dict(row) for row in rows]


def delete_analysis(db: Session, user: User, analysis_id: int) -> bool:
    # Filtering on user_id means users can only delete their own entries
    analysis = db.scalar(
        select(Analysis).where(Analysis.user_id == user.id, Analysis.id == analysis_id)
    )

    if analysis is None:
        return False

    plant_id = analysis.plant_id

    db.delete(analysis)
    db.flush()

    # A plant with no checks left is just clutter, so remove it too
    remaining = db.scalar(
        select(func.count()).select_from(Analysis).where(Analysis.plant_id == plant_id)
    )

    if remaining == 0:
        db.delete(db.get(Plant, plant_id))

    db.commit()

    return True


def clear_history(db: Session, user: User, person_id: int | None = None) -> None:
    query = select(Analysis).where(Analysis.user_id == user.id)

    if person_id is not None:
        query = query.where(Analysis.person_id == person_id)

    analyses = db.scalars(query).all()

    for analysis in analyses:
        db.delete(analysis)

    db.flush()

    # Remove plants that have no checks left (they are empty shells)
    plants = select(Plant).where(Plant.user_id == user.id)

    if person_id is not None:
        plants = plants.where(Plant.person_id == person_id)

    for plant in db.scalars(plants).all():
        checks = db.scalar(
            select(func.count()).select_from(Analysis).where(Analysis.plant_id == plant.id)
        )

        if checks == 0:
            db.delete(plant)

    db.commit()
