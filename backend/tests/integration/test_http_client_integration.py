import pytest
import respx
import httpx

from backend.adapters.outbound.partners.http_client import post_partner_async


@pytest.mark.asyncio
async def test_http_client_success_and_http_error():
    ok_url = "http://example.test/ok"
    err_url = "http://example.test/err"

    with respx.mock(assert_all_called=True) as mock:
        route_ok = mock.post(ok_url).mock(return_value=httpx.Response(200, text="OK"))
        route_err = mock.post(err_url).mock(return_value=httpx.Response(500, text="ERR"))

        ok_res = await post_partner_async(ok_url)
        err_res = await post_partner_async(err_url)

        assert route_ok.called
        assert route_err.called

        assert ok_res.url == ok_url
        assert ok_res.status_code == 200
        assert ok_res.bytes == 2
        assert ok_res.error is None

        assert err_res.url == err_url
        assert err_res.status_code == 500
        assert err_res.bytes is None
        assert isinstance(err_res.error, str) and err_res.error


@pytest.mark.asyncio
async def test_http_client_request_error():
    timeout_url = "http://example.test/timeout"

    with respx.mock(assert_all_called=True) as mock:
        req = httpx.Request("POST", timeout_url)
        mock.post(timeout_url).mock(side_effect=httpx.ConnectError("boom", request=req))

        res = await post_partner_async(timeout_url)

        assert res.url == timeout_url
        assert res.status_code is None
        assert res.bytes is None
        assert "boom" in (res.error or "")
