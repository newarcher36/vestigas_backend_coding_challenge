from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.adapters.scheduling.job_status import JobStatus
from backend.adapters.repostory.jobs.job_repository import JobsRepository
from backend.adapters.repostory.jobs.job_model import Base, JobModel


def test_create_job_persists_record(tmp_path):
    database_path = tmp_path / "jobs_repository.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    job_id = uuid4()
    status = JobStatus.PROCESSING
    created_at = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    updated_at = datetime(2024, 1, 1, 12, 5, tzinfo=timezone.utc)
    input_payload = {"site_id": "site-123", "partner_sources": ["Partner A"]}

    repository = JobsRepository(session_factory)
    returned_job_id = repository.create_job(
        job_id=job_id,
        status=status,
        created_at=created_at,
        updated_at=updated_at,
        input=input_payload,
        error=None,
    )

    assert returned_job_id == job_id

    with session_factory() as session:
        persisted_job = session.get(JobModel, str(job_id))

    assert persisted_job is not None
    assert persisted_job.status == status
    assert persisted_job.created_at == created_at.replace(tzinfo=None)
    assert persisted_job.updated_at == updated_at.replace(tzinfo=None)
    assert persisted_job.input == input_payload
    assert persisted_job.error is None
