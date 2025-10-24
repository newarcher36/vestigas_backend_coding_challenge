from __future__ import annotations

from functools import lru_cache
from typing import Mapping

from pydantic import ConfigDict, BaseModel

from backend.shared.config.settings import get_settings


class HttpConfig(BaseModel):
    timeout: float
    endpoints: Mapping[str, str]

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

@lru_cache
def get_http_config() -> HttpConfig:
    settings = get_settings()
    return HttpConfig(
        timeout=settings.http_timeout,
        endpoints=settings.partner_endpoints,
    )
