from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from backend.application.use_cases.fetch_deliveries import FetchPartnerDeliveriesUseCase
from backend.domain.partner_delivery import PartnerDelivery
from domain.stats import Stats


def test_fetch_partner_deliveries_use_case_fetches_and_processes_partner_delivery():
    fetched_at = datetime(2024, 1, 15, tzinfo=timezone.utc)
    partner_delivery = PartnerDelivery(delivery_data=[{"delivery_id": "xyz"}])
    expected_stats = Stats.for_partner("Partner A")

    fetch_port = MagicMock()
    fetch_port.fetch.return_value = partner_delivery
    mapper = MagicMock()

    with patch("backend.application.use_cases.fetch_deliveries.PartnerDeliveryProcessor") as mock_processor_cls:
        mock_processor_instance = mock_processor_cls.return_value
        mock_processor_instance.process.return_value = ([], expected_stats)

        use_case = FetchPartnerDeliveriesUseCase(
            fetch_partner_deliveries_port=fetch_port,
            partner_delivery_mapper=mapper,
        )

        result = use_case.fetch_partner_deliveries("site-123", fetched_at, "Partner A")

    fetch_port.fetch.assert_called_once_with("Partner A")
    mock_processor_cls.assert_called_once_with(mapper)
    mock_processor_instance.process.assert_called_once_with(
        delivery=partner_delivery,
        source="Partner A",
        site_id="site-123",
        fetched_at=fetched_at,
    )
    assert result is expected_stats
