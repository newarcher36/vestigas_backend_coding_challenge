from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from uuid import UUID

from backend.adapters.scheduling.job_status import JobStatus
from backend.domain.stats import Stats


class JobsPort(ABC):
    """Defines the contract for persisting job metadata."""

    @abstractmethod
    def create_job(self, job_id: UUID, status: JobStatus, created_at: datetime, updated_at: datetime, input: dict[str, str]) -> UUID:
        """Persist a new job and return its identifier."""
        pass

    @abstractmethod
    def update_job_stats(self, job_id: UUID, stats: Stats, updated_at: datetime, error: str | None = None) -> None:
        """Update stats, error message, and timestamp for a persisted job."""
        pass

    @abstractmethod
    def list_jobs(self, limit: int, offset: int) -> tuple[list[dict[str, Any]], int]:
        """Return a paginated collection of persisted jobs and the overall total."""
        pass
