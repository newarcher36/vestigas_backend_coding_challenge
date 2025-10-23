from __future__ import annotations

from functools import lru_cache
from typing import Mapping

from fastapi import Depends
from pydantic import BaseModel, ConfigDict

from backend.shared.config.settings import Settings, get_settings


class HttpConfig(BaseModel):
    timeout: float
    endpoints: Mapping[str, str]

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)


@lru_cache
def get_http_config(settings: Settings = Depends(get_settings)) -> HttpConfig:
    return HttpConfig(
        timeout=settings.http_timeout,
        endpoints=settings.partner_endpoints,
    )
