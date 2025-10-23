from __future__ import annotations

import pytest
import respx
from httpx import Response

from backend.adapters.outbound.partners.fetch_partner_deliveries_http_adapter import (
    FetchPartnerDeliveriesHttpAdapter,
)
from backend.adapters.outbound.partners.http_config import HttpConfig
from backend.domain.partner_delivery_fetch_error import PartnerDeliveryFetchError


def test_fetch_partner_deliveries_http_adapter_integration_success():
    http_config = HttpConfig(
        timeout=1.0,
        endpoints={"Partner A": "https://partner-a.test"},
    )
    adapter = FetchPartnerDeliveriesHttpAdapter(http_config=http_config)

    payload = {
        "deliveryId": "DEL-001-A",
        "supplier": "SupplierX",
    }

    with respx.mock(assert_all_called=True) as respx_mock:
        route = respx_mock.post("https://partner-a.test").mock(
            return_value=Response(200, json=payload),
        )
        deliveries = adapter.fetch_partner_deliveries("Partner A")

    assert route.called
    assert len(deliveries) == 1
    assert deliveries[0].source == "Partner A"
    assert deliveries[0].delivery_data == payload


def test_fetch_partner_deliveries_http_adapter_integration_http_error():
    http_config = HttpConfig(
        timeout=1.0,
        endpoints={"Partner B": "https://partner-b.test"},
    )
    adapter = FetchPartnerDeliveriesHttpAdapter(http_config=http_config)

    with respx.mock(assert_all_called=True) as respx_mock:
        respx_mock.post("https://partner-b.test").mock(return_value=Response(503))

        with pytest.raises(PartnerDeliveryFetchError) as exc_info:
            adapter.fetch_partner_deliveries("Partner B")

    assert "Failed to fetch deliveries from Partner B" in str(exc_info.value)
