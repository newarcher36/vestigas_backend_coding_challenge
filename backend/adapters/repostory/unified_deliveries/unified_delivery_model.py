from __future__ import annotations

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.adapters.repostory.jobs.job_model import Base


class UnifiedDeliveryModel(Base):
    """SQLAlchemy model representing a stored unified delivery."""

    __tablename__ = "unified_deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    delivery_id: Mapped[str] = mapped_column(String(128), nullable=False)
    supplier: Mapped[str] = mapped_column(String(128), nullable=False)
    delivered_at: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    signed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    site_id: Mapped[str] = mapped_column(String(128), nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    delivery_score: Mapped[float] = mapped_column(Float, nullable=False)
