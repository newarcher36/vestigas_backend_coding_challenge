from datetime import datetime, timezone
from functools import lru_cache


class Clock:
    def get_utc_now(self) -> datetime:
        return datetime.now(timezone.utc)


@lru_cache
def get_utc_clock() -> Clock:
    """Return the shared UtcMidnightToday singleton."""
    return Clock()
