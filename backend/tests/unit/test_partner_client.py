import pytest
from unittest.mock import AsyncMock, patch, Mock
import httpx
from backend.adapters.outbound.partners import http_client as partner_client


@pytest.mark.asyncio
async def test_post_partner_async_success():
    # Fake response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.content = b"{}"

    # AsyncClient mock as async context manager
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = False
    mock_client.post.return_value = mock_response

    with patch.object(partner_client.httpx, "AsyncClient", return_value=mock_client):
        res = await partner_client.post_partner_async("http://example/success")

        assert res.url == "http://example/success"
        assert res.status_code == 200
        assert res.bytes == 2
        assert res.error is None

        mock_client.post.assert_called_once_with("http://example/success")


@pytest.mark.asyncio
async def test_post_partner_async_failure_with_status_code():
    # Configure client to return 500 so raise_for_status triggers HTTPStatusError
    request = httpx.Request("POST", "http://example/fail")
    response = httpx.Response(500, request=request)
    http_err = httpx.HTTPStatusError("boom", request=request, response=response)

    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.content = b"err"
    mock_response.raise_for_status.side_effect = http_err

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = False
    mock_client.post.return_value = mock_response

    with patch.object(partner_client.httpx, "AsyncClient", return_value=mock_client):
        res = await partner_client.post_partner_async("http://example/fail")

        assert res.url == "http://example/fail"
        assert res.status_code == 500
        assert res.bytes is None
        assert res.error is "boom"

        mock_client.post.assert_called_once_with("http://example/fail")


@pytest.mark.asyncio
async def test_post_partner_async_request_error():
    # Simulate a network/timeout error (no HTTP response)
    request = httpx.Request("POST", "http://example/timeout")
    req_err = httpx.RequestError("timeout", request=request)

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = False
    mock_client.post.side_effect = req_err

    with patch.object(partner_client.httpx, "AsyncClient", return_value=mock_client):
        res = await partner_client.post_partner_async("http://example/timeout")

        assert res.url == "http://example/timeout"
        assert res.status_code is None
        assert res.bytes is None
        assert "timeout" in (res.error or "")

        mock_client.post.assert_called_once_with("http://example/timeout")


@pytest.mark.asyncio
async def test_post_partner_async_unexpected_exception():
    # Simulate an unexpected exception
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = False
    mock_client.post.side_effect = RuntimeError("boom")

    with patch.object(partner_client.httpx, "AsyncClient", return_value=mock_client):
        res = await partner_client.post_partner_async("http://example/boom")

        assert res.url == "http://example/boom"
        assert res.status_code is None
        assert res.bytes is None
        assert "boom" in (res.error or "")

        mock_client.post.assert_called_once_with("http://example/boom")
