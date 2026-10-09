import time

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Person, User
from app.security import DUMMY_HASH, hash_password, verify_password


class EmailAlreadyRegistered(Exception):
    pass


class InvalidCredentials(Exception):
    pass


class TooManyAttempts(Exception):
    pass


# --- Simple brute-force protection (in memory, resets when the server restarts) ---
MAX_FAILED_LOGINS = 5
LOCK_SECONDS = 15 * 60
_failed_logins: dict[str, list[float]] = {}


def _recent_failures(key: str) -> list[float]:
    cutoff = time.time() - LOCK_SECONDS
    recent = [t for t in _failed_logins.get(key, []) if t > cutoff]
    _failed_logins[key] = recent
    return recent


def register_user(db: Session, name: str, email: str, password: str) -> User:

    if db.scalar(select(User).where(User.email == email)):
        raise EmailAlreadyRegistered()

    user = User(name=name, email=email, password_hash=hash_password(password))
    db.add(user)

    try:
        db.flush()   # assigns user.id

        # Start with one person (the account owner) so there is always someone to select
        db.add(Person(owner_id=user.id, name=name))
        db.commit()
    except IntegrityError:
        # Two sign-ups with the same email at the same moment
        db.rollback()
        raise EmailAlreadyRegistered()

    return user


def authenticate(db: Session, email: str, password: str, client_ip: str) -> User:
    key = f"{client_ip}|{email}"

    if len(_recent_failures(key)) >= MAX_FAILED_LOGINS:
        raise TooManyAttempts()

    user = db.scalar(select(User).where(User.email == email))

    # Always run one hash check, even for unknown emails, so timing is similar
    password_ok = verify_password(
        password,
        user.password_hash if user else DUMMY_HASH
    )

    if user is None or not password_ok:
        _failed_logins.setdefault(key, []).append(time.time())
        raise InvalidCredentials()

    _failed_logins.pop(key, None)

    return user
