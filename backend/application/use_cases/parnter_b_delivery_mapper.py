from __future__ import annotations

from typing import List

from backend.application.use_cases.partner_mapper_shared import to_iso8601_utc
from backend.domain.partner_delivery import PartnerDelivery
from backend.domain.unified_delivery import UnifiedDelivery


def _normalize_status(status_code: str) -> str:
    normalized_status = status_code.strip().lower()
    status_map = {
        "ok": "delivered",
        "failed": "cancelled",
    }
    return status_map[normalized_status] if normalized_status in status_map else "pending"


def _map_partner_b_delivery(partner_delivery: PartnerDelivery, site_id: str) -> UnifiedDelivery:
    """Map a single Partner B delivery entry into the unified delivery model."""
    payload = partner_delivery.delivery_data
    delivered_at = to_iso8601_utc(payload["deliveredAt"])
    receiver = payload.get("receiver") or {}
    signed = bool(receiver.get("signed"))

    unified_delivery = UnifiedDelivery(
        id=payload["id"],
        supplier=payload["provider"],
        delivered_at=delivered_at,
        status=_normalize_status(payload.get("statusCode", "")),
        signed=signed,
        siteId=site_id,
        source=partner_delivery.source,
    )
    return unified_delivery


def map_partner_b_response(partner_deliveries: List[PartnerDelivery], site_id: str) -> List[UnifiedDelivery]:
    """Map Partner B payload sequence into UnifiedDelivery instances."""
    return [_map_partner_b_delivery(partner_delivery, site_id) for partner_delivery in partner_deliveries]
