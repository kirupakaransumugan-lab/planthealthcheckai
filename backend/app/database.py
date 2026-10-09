import logging
from urllib.parse import quote_plus

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


logger = logging.getLogger(__name__)


# quote_plus keeps special characters in the password (@, :, /) from breaking the URL
DATABASE_URL = (
    f"mysql+pymysql://{quote_plus(DB_USER or '')}:{quote_plus(DB_PASSWORD or '')}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,    # drop dead connections instead of failing the request
    pool_recycle=1800      # MySQL closes idle connections, so renew them
)

SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency: one DB session per request, always closed."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def _add_column_if_missing(table: str, column: str, ddl: str) -> bool:
    """create_all never alters existing tables, so older tables get new columns here."""
    columns = {c["name"] for c in inspect(engine).get_columns(table)}

    if column in columns:
        return False

    with engine.begin() as connection:
        connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {ddl}"))

    logger.info("Added %s.%s column", table, column)
    return True


def _add_person_link(table: str) -> None:
    """Adds table.person_id (plants and analyses now belong to a person)."""
    if not _add_column_if_missing(table, "person_id", "person_id INT NULL"):
        return

    with engine.begin() as connection:
        connection.execute(text(f"ALTER TABLE {table} ADD INDEX ix_{table}_person_id (person_id)"))
        connection.execute(text(
            f"ALTER TABLE {table} ADD CONSTRAINT fk_{table}_person "
            "FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE"
        ))


def _backfill_people() -> None:
    """Moves plants/analyses saved before 'people' existed under a default person.

    Each account gets one person named after the account owner, so no
    existing history is lost.
    """
    from sqlalchemy import select, update

    from app.models import Analysis, Person, Plant, User

    with SessionLocal() as db:
        orphan_owner_ids = set(
            db.scalars(select(Plant.user_id).where(Plant.person_id.is_(None)))
        ) | set(
            db.scalars(select(Analysis.user_id).where(Analysis.person_id.is_(None)))
        )

        for owner_id in orphan_owner_ids:
            user = db.get(User, owner_id)
            person = db.scalar(
                select(Person).where(Person.owner_id == owner_id).order_by(Person.id).limit(1)
            )

            if person is None:
                person = Person(owner_id=owner_id, name=user.name)
                db.add(person)
                db.flush()

            for model in (Plant, Analysis):
                db.execute(
                    update(model)
                    .where(model.user_id == owner_id, model.person_id.is_(None))
                    .values(person_id=person.id)
                )

            logger.info("Moved existing data of user %s under person '%s'", owner_id, person.name)

        db.commit()


def init_db():
    """Create any missing tables and columns. Safe to run on every startup."""
    from app import models  # noqa: F401  (registers the tables on Base)

    try:
        Base.metadata.create_all(bind=engine)

        _add_column_if_missing("users", "password_hash", "password_hash VARCHAR(255) NULL")
        _add_person_link("plants")
        _add_person_link("analyses")
        _backfill_people()

        logger.info("Database tables are ready")
    except Exception:
        logger.exception("Could not prepare the database. Check DB_* values in .env")
