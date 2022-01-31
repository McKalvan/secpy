import unittest
from unittest.mock import patch, Mock
import os
import json

from secpy.core.ticker_company_exchange_map import TickerCompanyExchangeMap, CTEObject

MOCK_CTE_DATA = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "company_tickers_exchange.json")


class TickerCompanyExchangeMapTest(unittest.TestCase):

    @patch("secpy.core.network_client.requests.get")
    def test_lookup_ticker(self, mock_get):
        with open(MOCK_CTE_DATA, "r") as f:
            mock_get.return_value = Mock(ok=True)
            mock_get.return_value.json.return_value = json.load(f)
        ticker_company_exchange_map = TickerCompanyExchangeMap("/")
        actual_cte_object = ticker_company_exchange_map.lookup_ticker("MSFT")
        expected_cte_object = CTEObject([789019, "MICROSOFT CORP", "MSFT", "Nasdaq"])
        self.assertEqual(actual_cte_object, expected_cte_object)

    @patch("secpy.core.network_client.requests.get")
    def test_lookup_cik(self, mock_get):
        with open(MOCK_CTE_DATA, "r") as f:
            mock_get.return_value = Mock(ok=True)
            mock_get.return_value.json.return_value = json.load(f)

        ticker_company_exchange_map = TickerCompanyExchangeMap("/")
        actual_cte_object = ticker_company_exchange_map.lookup_cik("0000789019")
        expected_cte_object = CTEObject([789019, "MICROSOFT CORP", "MSFT", "Nasdaq"])
        self.assertEqual(actual_cte_object, expected_cte_object)


if __name__ == '__main__':
    unittest.main()
