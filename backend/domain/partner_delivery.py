from typing import Any, List

from pydantic import BaseModel


class PartnerDelivery(BaseModel):
    """Raw delivery data fetched from a specific partner source."""

    source: str
    delivery_data: List[dict[str, Any]]
