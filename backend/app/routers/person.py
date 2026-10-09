from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.person import (
    PeopleResponse,
    PersonCreate,
    PersonResponse,
    PersonUpdate,
)
from app.schemas.plant import SuccessResponse
from app.services import person_service


router = APIRouter(
    prefix="/api/people",
    tags=["People"]
)


NAME_TAKEN = "You already have a person with this name."
NOT_FOUND = "Person not found."


@router.get("", response_model=PeopleResponse)
def list_people(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    person_service.ensure_default_person(db, user)

    return {"people": person_service.list_people(db, user)}


@router.post("", status_code=201, response_model=PersonResponse)
def create_person(
    request: PersonCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        return {"person": person_service.create_person(db, user, request)}
    except person_service.PersonNameTaken:
        raise HTTPException(status_code=409, detail=NAME_TAKEN)


@router.put("/{person_id}", response_model=PersonResponse)
def update_person(
    person_id: int,
    request: PersonUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        return {"person": person_service.update_person(db, user, person_id, request)}
    except person_service.PersonNotFound:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    except person_service.PersonNameTaken:
        raise HTTPException(status_code=409, detail=NAME_TAKEN)


@router.delete("/{person_id}", response_model=SuccessResponse)
def delete_person(
    person_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        person_service.delete_person(db, user, person_id)
    except person_service.PersonNotFound:
        raise HTTPException(status_code=404, detail=NOT_FOUND)

    return {"success": True}
