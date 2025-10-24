from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

from backend.application.use_cases.fetch_deliveries import FetchPartnerDeliveriesUseCase
from backend.domain.partner_delivery import PartnerDelivery
from backend.domain.partner_delivery_fetch_error import PartnerDeliveryFetchError


def test_fetch_partner_deliveries_use_case_continues_on_partner_failure():
    partner_sources = {"Partner A", "Partner B"}
    expected_delivery = PartnerDelivery(source="Partner B", delivery_data=[{"delivery_id": "xyz"}])

    def fetch_side_effect(source: str):
        if source == "Partner A":
            raise PartnerDeliveryFetchError(source, "boom")
        if source == "Partner B":
            return [expected_delivery]
        raise AssertionError(f"Unexpected source {source}")

    port = MagicMock()
    port.fetch.side_effect = fetch_side_effect
    use_case = FetchPartnerDeliveriesUseCase(fetch_partner_deliveries_port=port)

    result = use_case.fetch_partner_deliveries("site-123", datetime.now(timezone.utc), partner_sources)

    assert port.fetch.call_count == 2
    assert result == [expected_delivery]
