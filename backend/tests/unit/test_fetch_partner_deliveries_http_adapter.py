from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from backend.adapters.outbound.partners.fetch_partner_deliveries_http_adapter import (
    PartnerDeliveriesHttpAdapter,
)
from backend.adapters.outbound.partners.http_config import HttpConfig
from backend.domain.partner_delivery import PartnerDelivery
from backend.domain.partner_delivery_fetch_error import PartnerDeliveryFetchError


def _build_adapter(*endpoints: SimpleNamespace) -> PartnerDeliveriesHttpAdapter:
    http_config = HttpConfig(
        timeout=5.0,
        endpoints={endpoint.name: endpoint.url for endpoint in endpoints},
    )
    return PartnerDeliveriesHttpAdapter(http_config=http_config)


def _patch_async_client(mock_client) -> patch:
    context_manager = MagicMock()
    context_manager.__aenter__ = AsyncMock(return_value=mock_client)
    context_manager.__aexit__ = AsyncMock(return_value=None)
    return patch("httpx.AsyncClient", return_value=context_manager)


def test_fetch_partner_deliveries_successful_response():
    endpoint = SimpleNamespace(name="Partner A", url="https://partner-a.test")
    adapter = _build_adapter(endpoint)

    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = [{"delivery_id": "123"}]

    client = MagicMock()
    client.post = AsyncMock(return_value=response)

    with _patch_async_client(client) as async_client_cls:
        deliveries = adapter.fetch("Partner A")

    async_client_cls.assert_called_once_with(timeout=5.0)
    client.post.assert_awaited_once_with("https://partner-a.test")
    assert isinstance(deliveries, PartnerDelivery)
    assert deliveries.delivery_data == [{"delivery_id": "123"}]


def test_fetch_partner_deliveries_http_status_error():
    endpoint = SimpleNamespace(name="Partner B", url="https://partner-b.test")
    adapter = _build_adapter(endpoint)

    request = httpx.Request("POST", endpoint.url)
    http_error = httpx.HTTPStatusError(
        message="bad response",
        request=request,
        response=httpx.Response(503, request=request),
    )

    response = MagicMock()
    response.raise_for_status.side_effect = http_error

    client = MagicMock()
    client.post = AsyncMock(return_value=response)

    with _patch_async_client(client):
        with pytest.raises(PartnerDeliveryFetchError) as exc_info:
            adapter.fetch("Partner B")

    client.post.assert_awaited_once_with("https://partner-b.test")
    assert exc_info.type is PartnerDeliveryFetchError
    assert str(exc_info.value) == f"Failed to fetch deliveries from {endpoint.name}: bad response"
    assert exc_info.value.detail == "bad response"
    assert exc_info.value.source == endpoint.name


def test_fetch_partner_deliveries_request_error():
    endpoint = SimpleNamespace(name="Partner C", url="https://partner-c.test")
    adapter = _build_adapter(endpoint)

    request_error = httpx.RequestError(
        message="connection lost",
        request=httpx.Request("POST", endpoint.url),
    )

    client = MagicMock()
    client.post = AsyncMock(side_effect=request_error)

    with _patch_async_client(client):
        with pytest.raises(PartnerDeliveryFetchError) as exc_info:
            adapter.fetch("Partner C")

    client.post.assert_awaited_once_with("https://partner-c.test")
    assert exc_info.type is PartnerDeliveryFetchError
    assert str(exc_info.value) == f"Failed to fetch deliveries from {endpoint.name}: connection lost"
    assert exc_info.value.detail == "connection lost"
    assert exc_info.value.source == endpoint.name


def test_fetch_partner_deliveries_unknown_source():
    adapter = _build_adapter()

    with pytest.raises(PartnerDeliveryFetchError) as exc_info:
        adapter.fetch("Partner X")

    assert str(exc_info.value) == "Failed to fetch deliveries from Partner X: Unknown partner source"
    assert exc_info.value.detail == "Unknown partner source"
    assert exc_info.value.source == "Partner X"
