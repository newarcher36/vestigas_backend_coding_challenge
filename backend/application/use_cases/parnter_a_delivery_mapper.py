from typing import List

from backend.application.use_cases.partner_mapper_shared import to_iso8601_utc
from backend.domain.partner_delivery import PartnerDelivery
from backend.domain.unified_delivery import UnifiedDelivery


def _normalize_status(status: str) -> str:
    normalized_status = status.strip().lower()
    return normalized_status if normalized_status in {"delivered", "cancelled", "pending"} else "pending"


def _map_partner_a_delivery(partner_delivery: PartnerDelivery, site_id: str) -> UnifiedDelivery:
    """Map a single Partner A delivery entry into the unified delivery model."""
    payload = partner_delivery.delivery_data
    delivered_at = to_iso8601_utc(payload["timestamp"])
    signed = bool(payload.get("signedBy"))
    unified_delivery = UnifiedDelivery(
        id=payload["deliveryId"],
        supplier=payload["supplier"],
        delivered_at=delivered_at,
        status=_normalize_status(payload.get("status", "")),
        signed=signed,
        siteId=site_id,
        source=partner_delivery.source,
    )
    return unified_delivery


def map_partner_a_response(partner_deliveries: List[PartnerDelivery], site_id: str) -> List[UnifiedDelivery]:
    """Map Partner A payload into UnifiedDelivery instances."""
    return [_map_partner_a_delivery(partner_delivery, site_id) for partner_delivery in partner_deliveries]
