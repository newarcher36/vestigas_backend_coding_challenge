import pytest
from backend.application.use_cases.fetch_deliveries import run_fetch_for_partners_async
from backend.adapters.outbound.partners.http_client import PartnerFetchResult


async def fake_fetch(url: str) -> PartnerFetchResult:
    return PartnerFetchResult(url=url, status_code=200, bytes=1, error=None)


@pytest.mark.asyncio
async def test_run_fetch_for_partners_async_collects_results():
    urls = ["http://a", "http://b"]
    results = await run_fetch_for_partners_async(urls, fetch_fn=fake_fetch)

    assert len(results) == 2
    got = sorted(r.url for r in results)
    assert got == ["http://a", "http://b"]


async def fake_fetch_fail(url: str) -> PartnerFetchResult:
    if url.endswith("b"):
        # simulate failure by raising (use case should wrap into error result)
        raise RuntimeError("network error")
    return PartnerFetchResult(url=url, status_code=200, bytes=1, error=None)


@pytest.mark.asyncio
async def test_run_fetch_for_partners_async_handles_failures():
    urls = ["http://a", "http://b"]
    results = await run_fetch_for_partners_async(urls, fetch_fn=fake_fetch_fail)

    assert len(results) == 2
    res_by_url = {r.url: r for r in results}
    assert res_by_url["http://a"].error is None and res_by_url["http://a"].status_code == 200
    assert res_by_url["http://b"].error is not None and res_by_url["http://b"].status_code is None
