import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.config import JWT_EXPIRE_HOURS, JWT_SECRET


JWT_ALGORITHM = "HS256"


def check_password_strength(password: str) -> str | None:
    """Returns an error message if the password is too weak, otherwise None."""

    # TODO(human): decide how strict passwords must be (see the request in chat)
    if len(password) < 8:
        return "Password must be at least 8 characters long."

    return None


def hash_password(password: str) -> str:
    """scrypt (built into Python) with a random salt per password."""
    salt = os.urandom(16)

    digest = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32
    )

    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str | None) -> bool:
    if not stored_hash:
        return False

    try:
        scheme, salt_hex, digest_hex = stored_hash.split("$")

        if scheme != "scrypt":
            return False

        digest = hashlib.scrypt(
            password.encode("utf-8"),
            salt=bytes.fromhex(salt_hex),
            n=2**14, r=8, p=1, dklen=32
        )
    except (ValueError, TypeError):
        return False

    # Constant-time comparison so response timing can't leak the hash
    return hmac.compare_digest(digest.hex(), digest_hex)


# Verified against when an email is unknown, so "no such user" and
# "wrong password" take about the same time
DUMMY_HASH = hash_password(secrets.token_urlsafe(16))


def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(hours=JWT_EXPIRE_HOURS)
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> int | None:
    """Returns the user id, or None if the token is invalid or expired."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
