from __future__ import annotations

from unittest.mock import MagicMock, patch

from backend.application.use_cases.fetch_deliveries import FetchPartnerDeliveriesUseCase
from backend.domain.partner_delivery import PartnerDelivery
from backend.domain.stats import Stats


def test_fetch_partner_deliveries_use_case_fetches_and_processes_partner_delivery():
    partner_delivery = PartnerDelivery(delivery_data=[{"delivery_id": "xyz"}])
    expected_stats = Stats.for_partner("Partner A")

    fetch_port = MagicMock()
    fetch_port.fetch.return_value = partner_delivery
    mapper = MagicMock()

    with patch("backend.application.use_cases.fetch_deliveries.PartnerDeliveryProcessor") as mock_processor_cls:
        mock_processor_instance = mock_processor_cls.return_value
        expected_unified_deliveries = []
        mock_processor_instance.process.return_value = (expected_unified_deliveries, expected_stats)

        use_case = FetchPartnerDeliveriesUseCase(
            fetch_partner_deliveries_port=fetch_port,
            partner_delivery_mapper=mapper,
        )

        stats, unified_deliveries = use_case.fetch_partner_deliveries("site-123", "Partner A")

    fetch_port.fetch.assert_called_once_with("Partner A")
    mock_processor_cls.assert_called_once_with(mapper)
    mock_processor_instance.process.assert_called_once_with(
        delivery=partner_delivery,
        source="Partner A",
        site_id="site-123",
    )
    assert stats is expected_stats
    assert unified_deliveries is expected_unified_deliveries
