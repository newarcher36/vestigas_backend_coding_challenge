from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, Field


class PartnerStats(BaseModel):
    """Statistics collected while processing deliveries for a single partner."""

    fetched: int = 0
    transformed: int = 0
    errors: int = 0

    model_config = {"validate_assignment": True}

    def increment(self, field: str, amount: int = 1) -> None:
        current_value = getattr(self, field, None)
        if current_value is None:
            raise AttributeError(f"Invalid stats field: {field}")
        setattr(self, field, current_value + amount)


class Stats(BaseModel):
    """Aggregated statistics for a delivery fetch job."""

    partners: Dict[str, PartnerStats] = Field(default_factory=dict)
    stored: int = 0

    model_config = {"validate_assignment": True}

    def for_partner(self, partner: str) -> PartnerStats:
        """Return the partner stats instance, creating it on first access."""
        if partner not in self.partners:
            self.partners[partner] = PartnerStats()
        return self.partners[partner]

    def record_fetched(self, partner: str, count: int = 1) -> None:
        self.for_partner(partner).increment("fetched", count)

    def record_transformed(self, partner: str, count: int = 1) -> None:
        self.for_partner(partner).increment("transformed", count)

    def record_errors(self, partner: str, count: int = 1) -> None:
        self.for_partner(partner).increment("errors", count)

    def record_stored(self, count: int = 1) -> None:
        self.stored += count

    def as_dict(self) -> dict[str, object]:
        """Return a serialisable representation aligned with the assignment contract."""
        payload: dict[str, object] = {
            partner: stats.model_dump() for partner, stats in self.partners.items()
        }
        payload["stored"] = self.stored
        return payload
