from datetime import timezone

from dateutil.parser import isoparse


def to_iso8601_utc(date_str: str) -> str:
    """
    Parse an ISO 8601 datetime string and return it normalized to UTC (ending with 'Z').
    Only accepts strings that explicitly include timezone information.
    """
    try:
        dt = isoparse(date_str)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid ISO 8601 date string: {date_str!r}")

    # Reject if no timezone info
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError(f"Datetime string must include timezone info: {date_str!r}")

    # Convert to UTC
    dt_utc = dt.astimezone(timezone.utc)

    # Format as ISO 8601 string ending with 'Z'
    return dt_utc.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")