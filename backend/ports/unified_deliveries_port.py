from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from backend.domain.unified_delivery import UnifiedDelivery


class UnifiedDeliveriesPort(ABC):
    """Port defining persistence operations for unified deliveries."""

    @abstractmethod
    def store(self, job_id: UUID, unified_delivery: UnifiedDelivery) -> None:
        """Persist a single unified delivery for the given job."""
        raise NotImplementedError
