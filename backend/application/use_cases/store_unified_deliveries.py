from __future__ import annotations

from functools import lru_cache
from typing import Sequence
from uuid import UUID

from fastapi import Depends

from backend.adapters.repostory.unified_deliveries.unified_delivery_repository import (
    get_unified_deliveries_port,
)
from backend.domain.unified_delivery import UnifiedDelivery
from backend.ports.unified_deliveries_port import UnifiedDeliveriesPort


class StoreUnifiedDeliveriesUseCase:
    def __init__(self, unified_deliveries_port: UnifiedDeliveriesPort) -> None:
        self._unified_deliveries_port = unified_deliveries_port

    def store(self, job_id: UUID, unified_deliveries: Sequence[UnifiedDelivery]) -> None:
        for delivery in unified_deliveries:
            self._unified_deliveries_port.store(job_id, delivery)


@lru_cache
def get_store_unified_deliveries_use_case(
    unified_deliveries_port: UnifiedDeliveriesPort = Depends(get_unified_deliveries_port),
) -> StoreUnifiedDeliveriesUseCase:
    return StoreUnifiedDeliveriesUseCase(unified_deliveries_port)
