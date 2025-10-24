from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Mapping
from uuid import UUID

from backend.adapters.scheduling.job_status import JobStatus


class JobsPort(ABC):
    """Defines the contract for persisting job metadata."""

    @abstractmethod
    def create_job(
        self,
        job_id: UUID,
        status: JobStatus,
        createdAt: datetime,
        updatedAt: datetime,
        input: Mapping[str, Any],
        error: str | None,
    ) -> UUID:
        """Persist a new job and return its identifier."""
        pass
