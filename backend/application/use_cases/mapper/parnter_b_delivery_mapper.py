from __future__ import annotations

from typing import Any

from backend.domain.unified_delivery import UnifiedDelivery
from backend.shared.utils.date_utils import to_iso8601_utc


def _normalize_status(status_code: str) -> str:
    normalized_status = status_code.strip().lower()
    status_map = {
        "ok": "delivered",
        "failed": "cancelled",
    }
    return status_map[normalized_status] if normalized_status in status_map else "pending"


def extract_signed_delivery(delivery_data: dict[str, Any]) -> bool:
    receiver = delivery_data.get("receiver") or {}
    return bool(receiver.get("signed"))


def map_partner_delivery_b(source: str, site_id: str, delivery_data: dict[str, Any]) -> UnifiedDelivery:
    """Map Partner B payload into UnifiedDelivery instances using the shared mapper."""
    return UnifiedDelivery(
        id=delivery_data["id"],
        supplier=delivery_data["provider"],
        delivered_at=to_iso8601_utc(delivery_data.get("deliveredAt")),
        status=_normalize_status(delivery_data.get("statusCode", "")),
        signed=extract_signed_delivery(delivery_data),
        siteId=site_id,
        source=source,
    )
