from secpy.core.mixins.base_network_client_mixin import BaseNetworkClientMixin, EndpointEnum
from enum import Enum

from secpy.core.utils.cik_opts import CIKOpts


class TickerCompanyExchangeMap(BaseNetworkClientMixin):
    UNKNOWN = "UNKNOWN"
    CIK_LENGTH = 10

    def __init__(self, user_agent, **kwargs):
        """
        Handles downloading/parsing of company_tickers_exchange.json file from SEC REST API into a map of ticker -> CTEObject
        Used throughout to convert between CIK -> ticker values

        Important Note: Unlisted companies will not appear in this mapping they do not typically appear in company_tickers_exhcnage.json
        @param user_agent: Used in header of request to identify application making the request
        @param kwargs:
        """
        super().__init__(user_agent, **kwargs)
        self.__ticker_to_cte_object_mapping = None

    def lookup_ticker(self, ticker):
        """
        Search the __ticker_to_cte_object_mapping for a ticker, downloads company_tickers_exchange.json if it doesn't exist
        @param ticker: ticker to look up in map
        @return: CTEObject
        """
        self.__build_ticker_to_cte_object_mapping_if_none()
        return self.__ticker_to_cte_object_mapping[ticker]

    def lookup_cik(self, cik):
        """
        Search the __ticker_to_cte_object_mapping for a CIK, downloads company_tickers_exchange.json if it doesn't exist
        @param cik: cik to look up in map
        @return: CTEObject
        """
        self.__build_ticker_to_cte_object_mapping_if_none()
        find = [cte_object for cte_object in self.__ticker_to_cte_object_mapping.values() if cte_object.cik == cik]
        if find:
            return find[0]
        else:
            return self.UNKNOWN

    def filter_companies_by_exchange(self, exchange_enum):
        """
        Filters __ticker_to_cte_object_mapping into a mapping of only CTEObjects that are a part of the specified exchange
        @param exchange_enum: ExchangeEnum value defining what exchange to filter on
        @return: dictionary of ticker -> CTEObject where all CTEObject.exchange == exchange_enum.value
        """
        self.__build_ticker_to_cte_object_mapping_if_none()
        return {_: v for _, v in self.__ticker_to_cte_object_mapping.items() if v.exchange == exchange_enum.value}

    def ticker_to_cik_mapping(self):
        """
        Lists a mapping between ticker -> cik for each company
        @return:
        """
        self.__build_ticker_to_cte_object_mapping_if_none()
        return {_: v.cik for _, v in self.__ticker_to_cte_object_mapping.items()}

    def list_tickers(self):
        """
        Lists all tickers in the mapping
        @return: List[str]
        """
        self.__build_ticker_to_cte_object_mapping_if_none()
        return list(self.__ticker_to_cte_object_mapping.keys())

    def list_names(self):
        """
        Lists all companies in the mapping
        @return: List[str]
        """
        self.__build_ticker_to_cte_object_mapping_if_none()
        return [obj.name for obj in self.__ticker_to_cte_object_mapping.values() if obj.name != ""]

    def list_ciks(self):
        """
        Lists all ciks in the mapping
        @return: List[str]
        """
        self.__build_ticker_to_cte_object_mapping_if_none()
        return [obj.cik for obj in self.__ticker_to_cte_object_mapping.values()]

    def __build_ticker_to_cte_object_mapping_if_none(self):
        if not self.__ticker_to_cte_object_mapping:
            self.__build_ticker_to_cte_object_mapping()

    def __build_ticker_to_cte_object_mapping(self):
        response = self._validate_args_and_make_request(EndpointEnum.COMPANY_TICKER_EXCHANGE)
        response_data = response["data"]
        cte_objs = [CTEObject(obj) for obj in response_data]
        cik_to_ticker_mapping = {cte_obj.ticker: cte_obj for cte_obj in cte_objs}
        self.__ticker_to_cte_object_mapping = cik_to_ticker_mapping


class CTEObject:
    class CTESchemaEnum(Enum):
        """
        Each object in company_ticker_json is an array w/ 4 values, w/ each value representing one part of the schema
        """
        CIK = 0
        NAME = 1
        TICKER = 2
        EXCHANGE = 3

    def __init__(self, obj):
        """
        Data object class for storing data from the company_ticker_exchange.json endpoint
        CTE is short for Company Ticker Exchange.
        @param obj: dictionary to parse into CTEObject
        """
        self.cik = self.__set_cik(obj)
        self.ticker = obj[self.CTESchemaEnum.TICKER.value]
        self.exchange = obj[self.CTESchemaEnum.EXCHANGE.value]
        self.name = obj[self.CTESchemaEnum.NAME.value]

    def __set_cik(self, obj):
        cik_num = obj[self.CTESchemaEnum.CIK.value]
        return CIKOpts.format_cik(cik_num)

    def __eq__(self, other):
        if isinstance(other, CTEObject):
            return self.__dict__ == other.__dict__
        else:
            return False


class ExchangeEnum(Enum):
    """
    List of exchanges represented in the company_tickers_exchange.json file
    """
    NASDAQ = "Nasdaq"
    OTC = "OTC"
    CBOE = "CBOE"
    NYSE = "NYSE"
    NONE = ""
