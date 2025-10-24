from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from backend.adapters.scheduling.job_status import JobStatus
from domain.stats import Stats


class JobsPort(ABC):
    """Defines the contract for persisting job metadata."""

    @abstractmethod
    def create_job(self, job_id: UUID, status: JobStatus, created_at: datetime, updated_at: datetime, input: dict[str, str]) -> UUID:
        """Persist a new job and return its identifier."""
        pass

    @abstractmethod
    def update_job_stats(self, job_id: UUID, stats: Stats, error: str | None = None) -> None:
        """Update the stats payload and error message for a persisted job."""
        pass
