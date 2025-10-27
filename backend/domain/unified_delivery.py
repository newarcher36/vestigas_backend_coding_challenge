from __future__ import annotations

from datetime import datetime, time

from pydantic import BaseModel


class UnifiedDelivery(BaseModel):
    id: str
    supplier: str
    delivered_at: str
    status: str
    signed: bool
    siteId: str
    source: str

    model_config = {"populate_by_name": True, "frozen": True}

    @property
    def delivery_score(self) -> float:
        return compute_delivery_score(self.delivered_at, self.signed)


def compute_delivery_score(delivered_at: datetime, signed: bool) -> float:
    """Score deliveries based on signature and morning window."""
    morning_start = time(5, 0)
    morning_end = time(11, 0)
    in_morning_window = morning_start <= delivered_at.time() <= morning_end
    signature_score = 1.0 if signed else 0.3
    multiplier = 1.2 if in_morning_window else 1.0
    return round(signature_score * multiplier, 2)
