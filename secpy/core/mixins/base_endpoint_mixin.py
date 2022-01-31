import logging

from secpy.core.mixins.base_network_client_mixin import BaseNetworkClientMixin
from secpy.core.ticker_company_exchange_map import TickerCompanyExchangeMap


class BaseEndpointMixin(BaseNetworkClientMixin):
    _endpoint = None

    def __init__(self, user_agent, **kwargs):
        """
        Base class to be inherited by all classes that interact directly w/ the SEC REST API
        @param user_agent: unique identifiers to use in headers when making requests to SEC REST API
        @param kwargs: Misc
        """
        super().__init__(user_agent, **kwargs)
        self._logger = self.__set_logger()
        self._ticker_cte_map = TickerCompanyExchangeMap(user_agent, **kwargs)

    @staticmethod
    def __set_logger():
        logging.basicConfig(format="%(asctime)s-%(pathname)s-%(levelname)-%(message)s")
        return logging
