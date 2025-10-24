from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Iterable, List

from domain.stats import Stats
from domain.unified_delivery import UnifiedDelivery

from application.use_cases.mapper.partner_delivery_mapper import PartnerDeliveryMapper
from backend.domain.partner_delivery import PartnerDelivery

logger = logging.getLogger(__name__)


class PartnerDeliveryProcessor:
    def __init__(self, delivery_mapper: PartnerDeliveryMapper) -> None:
        self._delivery_mapper = delivery_mapper

    def process(
        self,
        *,
        delivery: PartnerDelivery,
        source: str,
        site_id: str,
        fetched_at: datetime,
    ) -> tuple[List[UnifiedDelivery], Stats]:
        stats = Stats.for_partner(source)
        unified_deliveries: List[UnifiedDelivery] = []
        for data in self._iterate_delivery_data(delivery):
            stats.record_fetched()
            try:
                unified_delivery = self._delivery_mapper.map(source, site_id, data)
                delivered_at = datetime.fromisoformat(unified_delivery.delivered_at)
                if delivered_at > fetched_at:
                    unified_deliveries.append(unified_delivery)
                    stats.record_transformed()
            except AttributeError:
                logger.error("Missing partner delivery mapper for delivery %s", delivery)
                stats.record_errors()
        return unified_deliveries, stats

    @staticmethod
    def _iterate_delivery_data(delivery: PartnerDelivery) -> Iterable[dict[str, Any]]:
        return delivery.delivery_data
