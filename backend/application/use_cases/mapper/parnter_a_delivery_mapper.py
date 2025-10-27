from typing import Any

from backend.domain.unified_delivery import UnifiedDelivery
from backend.shared.utils.date_utils import to_iso8601_utc


def _normalize_status(status: str) -> str:
    normalized_status = status.strip().lower()
    return normalized_status if normalized_status in {"delivered", "cancelled", "pending"} else "pending"


def map_partner_delivery_a(source: str, site_id: str, delivery_data: dict[str, Any]) -> UnifiedDelivery:
    """Map Partner A payload into UnifiedDelivery instances using the shared mapper."""
    return UnifiedDelivery(
        id=delivery_data["deliveryId"],
        supplier=delivery_data["supplier"],
        delivered_at=to_iso8601_utc(delivery_data.get("timestamp")),
        status=_normalize_status(delivery_data.get("status", "")),
        signed=bool(delivery_data.get("signedBy")),
        siteId=site_id,
        source=source,
    )
