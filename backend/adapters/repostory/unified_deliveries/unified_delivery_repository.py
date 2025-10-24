from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from typing import Any, Callable
from uuid import UUID

from fastapi import Depends
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from backend.adapters.repostory.jobs.job_model import Base
from backend.adapters.repostory.postgres_config import (
    PostgresConfig,
    get_postgres_config,
)
from backend.adapters.repostory.unified_deliveries.unified_delivery_model import (
    UnifiedDeliveryModel,
)
from backend.domain.unified_delivery import UnifiedDelivery, compute_delivery_score
from backend.ports.unified_deliveries_port import UnifiedDeliveriesPort


class UnifiedDeliveriesRepository(UnifiedDeliveriesPort):
    """Persist unified deliveries in a Postgres-backed table."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def store(self, job_id: UUID, unified_delivery: UnifiedDelivery) -> None:
        with self._session_factory() as session:
            model = self._to_model(job_id, unified_delivery)
            session.add(model)
            session.commit()

    def list_deliveries(self, limit: int, offset: int) -> tuple[list[dict[str, Any]], int]:
        with self._session_factory() as session:
            total = session.scalar(select(func.count()).select_from(UnifiedDeliveryModel)) or 0
            stmt = (
                select(UnifiedDeliveryModel)
                .order_by(UnifiedDeliveryModel.delivery_score.desc(), UnifiedDeliveryModel.id.asc())
                .offset(offset)
                .limit(limit)
            )
            deliveries = session.scalars(stmt).all()
            items: list[dict[str, Any]] = []
            for delivery in deliveries:
                items.append(
                    {
                        "jobId": delivery.job_id,
                        "id": delivery.delivery_id,
                        "supplier": delivery.supplier,
                        "deliveredAt": delivery.delivered_at,
                        "status": delivery.status,
                        "signed": delivery.signed,
                        "siteId": delivery.site_id,
                        "source": delivery.source,
                        "deliveryScore": float(delivery.delivery_score),
                    },
                )
        return items, total

    @staticmethod
    def _to_model(job_id: UUID, unified_delivery: UnifiedDelivery) -> UnifiedDeliveryModel:
        delivered_at = unified_delivery.delivered_at
        if isinstance(delivered_at, str):
            normalized = delivered_at.replace("Z", "+00:00")
            delivered_at_dt = datetime.fromisoformat(normalized)
        else:
            delivered_at_dt = delivered_at

        delivery_score = compute_delivery_score(delivered_at_dt, unified_delivery.signed)
        return UnifiedDeliveryModel(
            job_id=str(job_id),
            delivery_id=unified_delivery.id,
            supplier=unified_delivery.supplier,
            delivered_at=unified_delivery.delivered_at if isinstance(unified_delivery.delivered_at, str) else unified_delivery.delivered_at.isoformat(),
            status=unified_delivery.status,
            signed=unified_delivery.signed,
            site_id=unified_delivery.siteId,
            source=unified_delivery.source,
            delivery_score=delivery_score,
        )


def _build_session_factory(config: PostgresConfig) -> sessionmaker[Session]:
    engine = create_engine(config.postgres_dsn, future=True, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False, class_=Session)


@lru_cache
def get_unified_deliveries_port(
    config: PostgresConfig = Depends(get_postgres_config),
) -> UnifiedDeliveriesPort:
    session_factory = _build_session_factory(config)
    return UnifiedDeliveriesRepository(session_factory)
