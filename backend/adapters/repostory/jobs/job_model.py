from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, JSON, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from backend.adapters.scheduling.job_status import JobStatus


class Base(DeclarativeBase):
    """Declarative base for SQLAlchemy models."""


class JobModel(Base):
    __tablename__ = "jobs"

    id: Mapped[String] = mapped_column(String(36), primary_key=True)
    status: Mapped[JobStatus] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    input: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    stats: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)