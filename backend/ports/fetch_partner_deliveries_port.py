from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from backend.domain.partner_delivery import PartnerDelivery


class FetchPartnerDeliveriesPort(ABC):

    @abstractmethod
    def fetch_partner_deliveries(self, source: str) -> List[PartnerDelivery]:
        """Retrieve raw partner deliveries for the given partner source."""
        pass
