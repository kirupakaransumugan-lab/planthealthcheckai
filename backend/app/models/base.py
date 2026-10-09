from datetime import datetime, timezone


def utc_now() -> datetime:
    # MySQL DATETIME has no timezone, so store UTC without tzinfo
    return datetime.now(timezone.utc).replace(tzinfo=None)
