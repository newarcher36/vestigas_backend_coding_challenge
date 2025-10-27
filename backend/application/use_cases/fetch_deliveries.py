from __future__ import annotations

import logging
from functools import lru_cache
from typing import List, Tuple

from fastapi import Depends

from backend.application.use_cases.mapper.partner_delivery_mapper import (
    PartnerDeliveryMapper,
    get_partner_delivery_mapper,
)
from backend.application.use_cases.partner_delivery_processor import PartnerDeliveryProcessor
from backend.adapters.outbound.partners.fetch_partner_deliveries_http_adapter import get_fetch_partner_deliveries_port
from backend.domain.partner_delivery import PartnerDelivery
from backend.ports.fetch_partner_deliveries_port import FetchPartnerDeliveriesPort
from backend.domain.stats import Stats
from backend.domain.unified_delivery import UnifiedDelivery

logger = logging.getLogger(__name__)


class FetchPartnerDeliveriesUseCase:
    def __init__(
            self,
            fetch_partner_deliveries_port: FetchPartnerDeliveriesPort,
            partner_delivery_mapper: PartnerDeliveryMapper
    ) -> None:
        self._fetch_partner_deliveries_port = fetch_partner_deliveries_port
        self._partner_delivery_mapper = partner_delivery_mapper
        self._partner_delivery_processor = PartnerDeliveryProcessor(partner_delivery_mapper)

    def fetch_partner_deliveries(
        self,
        site_id: str,
        source: str,
    ) -> Tuple[Stats, List[UnifiedDelivery]]:
        logger.info("Fetching partner deliveries for site %s from source %s", site_id, source)
        delivery: PartnerDelivery = self._fetch_partner_deliveries_port.fetch(source)
        unified_deliveries, stats = self._partner_delivery_processor.process(
            delivery=delivery,
            source=source,
            site_id=site_id,
        )
        return stats, unified_deliveries


@lru_cache
def get_fetch_partner_deliveries_use_case(
        fetch_partner_deliveries_port: FetchPartnerDeliveriesPort = Depends(get_fetch_partner_deliveries_port),
        partner_delivery_mapper: PartnerDeliveryMapper = Depends(get_partner_delivery_mapper)
) -> FetchPartnerDeliveriesUseCase:
    return FetchPartnerDeliveriesUseCase(fetch_partner_deliveries_port, partner_delivery_mapper)
