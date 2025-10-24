from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from typing import Callable
from uuid import UUID

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.adapters.scheduling.job_status import JobStatus
from backend.adapters.repostory.jobs.job_model import JobModel, Base
from backend.adapters.repostory.postgres_config import PostgresConfig, get_postgres_config
from backend.ports.jobs_port import JobsPort
from domain.stats import Stats


class JobsRepository(JobsPort):
    """Persist jobs in a Postgres-backed `jobs` table."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def create_job(self, job_id: UUID, status: JobStatus, created_at: datetime, updated_at: datetime, input: dict[str, str]) -> UUID:
        with self._session_factory() as session:
            job_model = JobModel(
                id=str(job_id),
                status=status,
                created_at=created_at,
                updated_at=updated_at,
                input=input,
                stats=None,
                error=None,
            )
            session.add(job_model)
            session.commit()
        return job_id

    def update_job_stats(self, job_id: UUID, stats: Stats, error: str | None = None) -> None:
        with self._session_factory() as session:
            job_model = session.get(JobModel, str(job_id))
            if job_model is None:
                raise ValueError(f"Job with id {job_id} does not exist.")
            job_model.stats = stats.as_dict()
            job_model.error = error
            session.commit()

def _build_session_factory(config: PostgresConfig) -> sessionmaker[Session]:
    engine = create_engine(config.postgres_dsn, future=True, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False, class_=Session)


@lru_cache
def get_jobs_port(config: PostgresConfig = Depends(get_postgres_config)) -> JobsPort:
    session_factory = _build_session_factory(config)
    return JobsRepository(session_factory)
