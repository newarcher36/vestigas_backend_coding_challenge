from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class PartnerDelivery(BaseModel):
    """Raw delivery data fetched from a specific partner source."""

    source: str
    delivery_data: dict[str, Any]
