from __future__ import annotations

from pydantic import BaseModel, Field

from backend.domain.stats_fields import StatsFields


class Stats(BaseModel):
    """Statistics collected while processing deliveries for a single partner."""

    partner: str
    stats: dict[StatsFields, int] = Field(
        default_factory=lambda: {
            StatsFields.FETCHED: 0,
            StatsFields.TRANSFORMED: 0,
            StatsFields.ERRORS: 0,
        },
    )
    stored: int = 0

    model_config = {"validate_assignment": True}

    @classmethod
    def for_partner(cls, partner: str) -> Stats:
        """Factory that initialises stats for a specific partner."""
        return cls(partner=partner)

    def _increment(self, field: StatsFields, amount: int) -> None:
        self.stats[field] += amount

    def record_fetched(self, count: int = 1) -> None:
        self._increment(StatsFields.FETCHED, count)

    def record_transformed(self, count: int = 1) -> None:
        self._increment(StatsFields.TRANSFORMED, count)

    def record_errors(self, count: int = 1) -> None:
        self._increment(StatsFields.ERRORS, count)

    def record_stored(self, count: int = 1) -> None:
        self.stored += count

    def as_dict(self) -> dict[str, object]:
        """Return a serialisable representation aligned with the assignment contract."""
        partner_stats = {
            StatsFields.FETCHED.value: self.stats[StatsFields.FETCHED],
            StatsFields.TRANSFORMED.value: self.stats[StatsFields.TRANSFORMED],
            StatsFields.ERRORS.value: self.stats[StatsFields.ERRORS],
        }
        return {self.partner: partner_stats, StatsFields.STORED.value: self.stored}
