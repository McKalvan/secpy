from pyedgar.utils.mixins.base_mixin import BaseMixin
from pyedgar.utils.network_client import NetworkClient, EndpointEnum
from enum import Enum

__CIK_LENGTH = 10


class TickerCTEMap(BaseMixin):

    UNKNOWN = "UNKNOWN"

    def __init__(self, network_client=None, **kwargs):
        super().__init__(network_client, **kwargs)
        self.__ticker_to_cte_object_mapping = None

    def lookup_ticker(self, ticker):
        self.__build_ticker_to_cte_object_mapping_if_none()
        return self.__ticker_to_cte_object_mapping[ticker]

    # TODO: This seems inefficient, see if there is a better way to do this
    def lookup_cik(self, cik):
        self.__build_ticker_to_cte_object_mapping_if_none()
        find = [cte_object for cte_object in self.__ticker_to_cte_object_mapping.values() if cte_object.cik == cik]
        if find:
            return find[0]
        else:
            return self.UNKNOWN


    def filter_by_exchange(self, exchange_enum):
        self.__build_ticker_to_cte_object_mapping_if_none()
        return {_: v for _, v in self.__ticker_to_cte_object_mapping.items() if v.exchange == exchange_enum.value}

    def ticker_to_cik_mapping(self):
        self.__build_ticker_to_cte_object_mapping_if_none()
        return {_: v.cik for _, v in self.__ticker_to_cte_object_mapping.items()}

    def tickers(self):
        self.__build_ticker_to_cte_object_mapping_if_none()
        return list(self.__ticker_to_cte_object_mapping.keys())

    def names(self):
        self.__build_ticker_to_cte_object_mapping_if_none()
        return [obj.name for obj in self.__ticker_to_cte_object_mapping.values() if obj.name != ""]

    def ciks(self):
        self.__build_ticker_to_cte_object_mapping_if_none()
        return [obj.cik for obj in self.__ticker_to_cte_object_mapping.values()]

    def __build_ticker_to_cte_object_mapping_if_none(self):
        if not self.__ticker_to_cte_object_mapping:
            self.build_ticker_to_cte_object_mapping()

    def build_ticker_to_cte_object_mapping(self):
        response = self._network_client.make_request(EndpointEnum.COMPANY_TICKER_EXCHANGE)
        response_data = response.json()["data"]
        cik_to_ticker_mapping = {obj[CTESchemaEnum.TICKER.value]: CTEObject(obj) for obj in response_data}
        self.__ticker_to_cte_object_mapping = cik_to_ticker_mapping
        return cik_to_ticker_mapping


class CTEObject:
    """
    Data object class for storing data from the company_ticker_exchange.json endpoint
    CTE is short for Company Ticker Exchange.
    """

    def __init__(self, obj):
        self.cik = self.set_cik(obj)
        self.ticker = obj[CTESchemaEnum.TICKER.value]
        self.exchange = obj[CTESchemaEnum.EXCHANGE.value]
        self.name = obj[CTESchemaEnum.NAME.value]

    @staticmethod
    def set_cik(obj):
        cik_num = obj[CTESchemaEnum.CIK.value]
        return format_cik(cik_num)

    def __str__(self):
        return "CIK: {CIK}, ticker: {TICKER}, exchange: {EXCHANGE}, name: {NAME}".format(
            CIK=self.cik,
            TICKER=self.ticker,
            EXCHANGE=self.exchange,
            NAME=self.name
        )


class CTESchemaEnum(Enum):
    CIK = 0
    NAME = 1
    TICKER = 2
    EXCHANGE = 3


class ExchangeEnum(Enum):
    NASDAQ = "Nasdaq"
    OTC = "OTC"
    CBOE = "CBOE"
    NYSE = "NYSE"
    NONE = ""


def format_cik(cik_num):
    formatted_cik = str(cik_num).zfill(__CIK_LENGTH)
    return formatted_cik

