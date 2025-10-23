from __future__ import annotations


class PartnerDeliveryFetchError(Exception):
    """Raised when fetching partner deliveries fails for a specific source."""

    def __init__(self, source: str, detail: str):
        self.source = source
        self.detail = detail
        message = f"Failed to fetch deliveries from {source}: {detail}"
        super().__init__(message)
