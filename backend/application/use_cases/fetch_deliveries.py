import logging
import asyncio
from typing import Callable, List, Awaitable

from backend.adapters.outbound.partners.http_client import (
    post_partner_async,
    PartnerFetchResult,
)

logger = logging.getLogger("uvicorn.error")


async def run_fetch_for_partners_async(
    urls: List[str],
    fetch_fn: Callable[[str], Awaitable[PartnerFetchResult]] = post_partner_async,
) -> List[PartnerFetchResult]:
    """Fetch all partner URLs concurrently using asyncio and return results."""

    async def safe_fetch(url: str) -> PartnerFetchResult:
        try: 
            return await fetch_fn(url)
        except Exception as e:
            return PartnerFetchResult(url=url, status_code=None, bytes=None, error=str(e))

    tasks = [asyncio.create_task(safe_fetch(u)) for u in urls]
    return await asyncio.gather(*tasks)


def run_fetch_for_partners(urls: List[str]) -> List[PartnerFetchResult]:
    """Synchronous wrapper to run async fetch from non-async contexts (e.g., scheduler)."""
    return asyncio.run(run_fetch_for_partners_async(urls))
