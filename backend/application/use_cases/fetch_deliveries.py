from __future__ import annotations

import logging
from datetime import datetime
from functools import lru_cache
from typing import List

from fastapi import Depends

from backend.adapters.outbound.partners.fetch_partner_deliveries_http_adapter import get_fetch_partner_deliveries_port
from backend.domain.partner_delivery import PartnerDelivery
from backend.domain.partner_delivery_fetch_error import PartnerDeliveryFetchError
from backend.ports.fetch_partner_deliveries_port import FetchPartnerDeliveriesPort

logger = logging.getLogger(__name__)


class FetchPartnerDeliveriesUseCase:
    def __init__(
            self,
            fetch_partner_deliveries_port: FetchPartnerDeliveriesPort
    ) -> None:
        self._fetch_partner_deliveries_port = fetch_partner_deliveries_port

    def fetch_partner_deliveries(self, site_id: str, fetched_at: datetime, partner_sources: set[str]) -> List[PartnerDelivery]:
        logger.info("Fetching partner deliveries for site %s : datetime %s : sources %s", site_id)
        deliveries: List[PartnerDelivery] = []
        for source in partner_sources:
            try:
                deliveries.extend(self._fetch_partner_deliveries_port.fetch(source))
            except PartnerDeliveryFetchError as exc:
                logger.error("Failed to fetch deliveries for source %s: %s", source, exc)
        return deliveries


@lru_cache
def get_fetch_partner_deliveries_use_case(fetch_partner_deliveries_port: FetchPartnerDeliveriesPort = Depends(get_fetch_partner_deliveries_port)) -> FetchPartnerDeliveriesUseCase:
    return FetchPartnerDeliveriesUseCase(fetch_partner_deliveries_port)
