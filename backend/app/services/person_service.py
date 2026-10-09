from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Analysis, Person, User
from app.schemas.person import PersonCreate


class PersonNotFound(Exception):
    pass


class PersonNameTaken(Exception):
    pass


def _to_dict(person: Person, analysis_count: int) -> dict:
    return {
        "id": person.id,
        "name": person.name,
        "location": person.location,
        "notes": person.notes,
        "analysis_count": analysis_count,
        "created_at": person.created_at.isoformat() + "Z"   # stored as UTC
    }


def get_person(db: Session, user: User, person_id: int) -> Person:
    """Loads a person, but only if they belong to this user."""

    person = db.scalar(
        select(Person).where(Person.id == person_id, Person.owner_id == user.id)
    )

    if person is None:
        raise PersonNotFound()

    return person


def ensure_default_person(db: Session, user: User) -> None:
    """Every account gets one person (named after the account owner) to start with."""

    has_person = db.scalar(select(Person.id).where(Person.owner_id == user.id).limit(1))

    if has_person is None:
        db.add(Person(owner_id=user.id, name=user.name))
        db.commit()


def list_people(db: Session, user: User) -> list[dict]:
    rows = db.execute(
        select(Person, func.count(Analysis.id))
        .outerjoin(Analysis, Analysis.person_id == Person.id)
        .where(Person.owner_id == user.id)
        .group_by(Person.id)
        .order_by(Person.name)
    ).all()

    return [_to_dict(person, count) for person, count in rows]


def _name_in_use(db: Session, user: User, name: str, ignore_id: int | None = None) -> bool:
    query = select(Person.id).where(Person.owner_id == user.id, Person.name == name)

    if ignore_id is not None:
        query = query.where(Person.id != ignore_id)

    return db.scalar(query.limit(1)) is not None


def create_person(db: Session, user: User, data: PersonCreate) -> dict:

    if _name_in_use(db, user, data.name):
        raise PersonNameTaken()

    person = Person(
        owner_id=user.id,
        name=data.name,
        location=data.location,
        notes=data.notes
    )

    db.add(person)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise PersonNameTaken()

    return _to_dict(person, 0)


def update_person(db: Session, user: User, person_id: int, data: PersonCreate) -> dict:
    person = get_person(db, user, person_id)

    if _name_in_use(db, user, data.name, ignore_id=person.id):
        raise PersonNameTaken()

    person.name = data.name
    person.location = data.location
    person.notes = data.notes

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise PersonNameTaken()

    count = db.scalar(
        select(func.count(Analysis.id)).where(Analysis.person_id == person.id)
    )

    return _to_dict(person, count)


def delete_person(db: Session, user: User, person_id: int) -> None:
    """Deletes the person together with their plants and saved checks."""

    person = get_person(db, user, person_id)

    db.delete(person)
    db.commit()
