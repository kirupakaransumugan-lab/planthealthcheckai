import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.plant import (
    HistoryResponse,
    PlantAnalysisRequest,
    PlantAnalysisResponse,
    SuccessResponse,
)
from app.services import history_service, person_service
from app.services.ai_service import analyze_plant


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/plant",
    tags=["Plant Analysis"]
)


@router.post("/analyze", response_model=PlantAnalysisResponse)
def analyze(
    request: PlantAnalysisRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    # Check the person first so no AI request is wasted on an invalid one
    try:
        person = person_service.get_person(db, user, request.person_id)
    except person_service.PersonNotFound:
        raise HTTPException(status_code=404, detail="Person not found.")

    try:
        result, model_used = analyze_plant(
            request.plant_name,
            request.plant_type,
            request.location,
            request.symptom
        )

    except Exception as e:
        # Log the real cause on the server only; the client gets a safe message
        logger.exception("Gemini analysis failed")

        if getattr(e, "code", None) == 429:
            raise HTTPException(
                status_code=429,
                detail="The AI usage limit has been reached. Please try again later."
            )

        raise HTTPException(
            status_code=500,
            detail="Unable to analyze the plant at this time."
        )

    # Saving must never make a successful analysis look like a failure
    analysis_id = None

    try:
        analysis_id = history_service.save_analysis(
            db, user, person, request, result, model_used
        ).id
    except Exception:
        db.rollback()
        logger.exception("Could not save the analysis to the database")

    return {
        "success": True,
        "analysis": result.model_dump(),
        "analysis_id": analysis_id,
        "saved": analysis_id is not None
    }


@router.get("/history", response_model=HistoryResponse)
def get_history(
    person_id: int | None = Query(default=None, description="Only this person's checks."),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return {"history": history_service.list_history(db, user, person_id)}


@router.delete("/history/{analysis_id}", response_model=SuccessResponse)
def delete_history_item(
    analysis_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not history_service.delete_analysis(db, user, analysis_id):
        raise HTTPException(
            status_code=404,
            detail="History item not found."
        )

    return {"success": True}


@router.delete("/history", response_model=SuccessResponse)
def clear_history(
    person_id: int | None = Query(default=None, description="Only clear this person's checks."),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    history_service.clear_history(db, user, person_id)

    return {"success": True}
