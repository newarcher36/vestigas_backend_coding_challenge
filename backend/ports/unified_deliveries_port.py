from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from backend.domain.unified_delivery import UnifiedDelivery


class UnifiedDeliveriesPort(ABC):
    """Port defining persistence operations for unified deliveries."""

    @abstractmethod
    def store(self, job_id: UUID, unified_delivery: UnifiedDelivery) -> None:
        """Persist a single unified delivery for the given job."""
        raise NotImplementedError

    @abstractmethod
    def list_deliveries(self, limit: int, offset: int) -> tuple[list[dict[str, Any]], int]:
        """Return a paginated list of stored unified deliveries and the overall total."""
        raise NotImplementedError
