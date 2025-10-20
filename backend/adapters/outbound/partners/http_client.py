import logging
from dataclasses import dataclass
from typing import Optional

import httpx

logger = logging.getLogger("uvicorn.error")


@dataclass
class PartnerFetchResult:
    url: str
    status_code: Optional[int]
    bytes: Optional[int]
    error: Optional[str]


async def post_partner_async(url: str, timeout: float = 5.0) -> PartnerFetchResult:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(url)
            r.raise_for_status()
            logger.info(f"Fetch from {url} -> status {r.status_code}, bytes={len(r.content)}")
            return PartnerFetchResult(url=url, status_code=r.status_code, bytes=len(r.content), error=None)

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP status error for {url}: {e}")
        return PartnerFetchResult(url=url, status_code=e.response.status_code, bytes=None, error=str(e))

    except httpx.RequestError as e:
        logger.error(f"Request error for {url}: {e}")
        return PartnerFetchResult(url=url, status_code=None, bytes=None, error=str(e))

    except Exception as e:
        logger.error(f"Unexpected error for {url}: {e}")
        return PartnerFetchResult(url=url, status_code=None, bytes=None, error=str(e))
