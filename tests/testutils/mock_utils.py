from unittest.mock import Mock, patch
import os.path
import json

from secpy.core.ticker_company_exchange_map import TickerCompanyExchangeMap

RESOURCES = os.path.join(os.path.dirname(__file__), "..", "resources")


@patch("secpy.core.network_client.requests.get")
def mock_company_tickers_exchange(mock_get):
    mock_cte_path = os.path.join(RESOURCES, "company_tickers_exchange.json")
    with open(mock_cte_path, "r") as f:
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = json.load(f)
        ticker_company_exchange_map = TickerCompanyExchangeMap("/")
        ticker_company_exchange_map.list_ciks()
        return ticker_company_exchange_map

