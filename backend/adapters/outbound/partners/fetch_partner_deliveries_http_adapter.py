from __future__ import annotations

import asyncio
import logging
from functools import lru_cache

import httpx

from backend.adapters.outbound.partners.http_config import HttpConfig, get_http_config
from backend.domain.partner_delivery import PartnerDelivery
from backend.domain.partner_delivery_fetch_error import PartnerDeliveryFetchError
from backend.ports.fetch_partner_deliveries_port import FetchPartnerDeliveriesPort

logger = logging.getLogger(__name__)


class PartnerDeliveriesHttpAdapter(FetchPartnerDeliveriesPort):
    def __init__(self, http_config: HttpConfig):
        self._timeout = http_config.timeout
        self.endpoints = http_config.endpoints

    async def _fetch_async(self, source: str, url: str) -> PartnerDelivery:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            logger.info("Fetching deliveries from %s", source)
            try:
                response = await client.post(url)
                response.raise_for_status()
                logger.debug("Response body: %s", response.text)
                return PartnerDelivery(delivery_data=response.json())
            except httpx.HTTPStatusError as exc:
                logger.error("HTTP error fetching deliveries from %s: %s", source, exc)
                raise PartnerDeliveryFetchError(source, str(exc)) from exc
            except httpx.RequestError as exc:
                logger.error("Request error fetching deliveries from %s: %s", source, exc)
                raise PartnerDeliveryFetchError(source, str(exc)) from exc
            except Exception as exc:
                logger.error("Unexpected error fetching deliveries from %s: %s", source, exc)
                raise PartnerDeliveryFetchError(source, str(exc)) from exc

    def fetch(self, source: str) -> PartnerDelivery:
        url = self.endpoints.get(source)
        if url is None:
            logger.error("Unknown partner source requested: %s", source)
            raise PartnerDeliveryFetchError(source, "Unknown partner source")
        return asyncio.run(self._fetch_async(source, url))

@lru_cache
def get_fetch_partner_deliveries_port() -> FetchPartnerDeliveriesPort:
    http_config: HttpConfig = get_http_config()
    return PartnerDeliveriesHttpAdapter(http_config=http_config)
