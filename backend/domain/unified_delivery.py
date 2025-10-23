from __future__ import annotations

from datetime import datetime, time

from pydantic import BaseModel, Field, model_validator


class UnifiedDelivery(BaseModel):
    id: str
    supplier: str
    deliveredAt: datetime = Field(alias="delivered_at")
    status: str
    signed: bool
    siteId: str
    source: str
    deliveryScore: float = Field(alias="delivery_score")

    model_config = {"populate_by_name": True, "frozen": True}

    @model_validator(mode="after")
    def set_delivery_score(self):
        object.__setattr__(self, "deliveryScore", compute_delivery_score(self.deliveredAt, self.signed))
        return self


def compute_delivery_score(delivered_at: datetime, signed: bool) -> float:
    """Score deliveries based on signature and morning window."""
    morning_start = time(5, 0)
    morning_end = time(11, 0)
    in_morning_window = morning_start <= delivered_at.time() <= morning_end
    signature_score = 1.0 if signed else 0.3
    multiplier = 1.2 if in_morning_window else 1.0
    return round(signature_score * multiplier, 2)
