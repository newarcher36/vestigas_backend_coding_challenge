from functools import lru_cache
from typing import Any, Callable

from backend.application.use_cases.mapper.parnter_a_delivery_mapper import map_partner_delivery_a
from backend.application.use_cases.mapper.parnter_b_delivery_mapper import map_partner_delivery_b
from backend.shared.config.settings import get_settings, Settings
from backend.domain.unified_delivery import UnifiedDelivery


class PartnerDeliveryMapper:
    def __init__(self, settings: Settings) -> None:
        self._mapper_by_source: dict[str, Callable[[str, str, dict[str, Any]], UnifiedDelivery]] = {
            settings.source_a: map_partner_delivery_a,
            settings.source_b: map_partner_delivery_b,
        }

    def map(self, source: str, site_id: str, delivery_data: dict[str, Any]) -> UnifiedDelivery:
        mapper = self._mapper_by_source.get(source)
        return mapper(source, site_id, delivery_data)

@lru_cache
def get_partner_delivery_mapper() -> PartnerDeliveryMapper:
    settings = get_settings()
    return PartnerDeliveryMapper(settings)
