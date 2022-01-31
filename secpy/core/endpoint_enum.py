from enum import Enum
from secpy.core.utils.cik_opts import CIKOpts
from secpy.core.utils.period_format_opts import PeriodFormatOpts


class EndpointEnum(Enum):
    """
    Specifies templates for all SEC REST API endpoints that are used in secpy
    """
    __BASE_SEC_URL = "https://www.sec.gov"
    __BASE_DATA_SEC_URL = "https://data.sec.gov"

    EDGAR_DATA_ARCHIVES = __BASE_SEC_URL + "/Archives/edgar/data/{CIK_NUM}/{ACCESSION_NUM}/{FILE_NAME}"
    COMPANY_TICKER_EXCHANGE = __BASE_SEC_URL + "/files/company_tickers_exchange.json"
    BULK_COMPANY_FACTS = __BASE_SEC_URL + "/Archives/edgar/daily-index/xbrl/companyfacts.zip"
    BULK_SUBMISSIONS = __BASE_SEC_URL + "/Archives/edgar/daily-index/bulkdata/submissions.zip"

    SUBMISSIONS = __BASE_DATA_SEC_URL + "/submissions/{FILE_NAME}"
    SUBMISSIONS_CIK = __BASE_DATA_SEC_URL + "/submissions/CIK{CIK}.json"

    COMPANY_CONCEPT = __BASE_DATA_SEC_URL + "/api/xbrl/companyconcept/CIK{CIK}/{TAXONOMY}/{CONCEPT}.json"
    COMPANY_FACTS = __BASE_DATA_SEC_URL + "/api/xbrl/companyfacts/CIK{CIK}.json"

    FRAMES = __BASE_DATA_SEC_URL + "/api/xbrl/frames/{TAXONOMY}/{CONCEPT}/{UNIT}/{PERIOD_FORMAT}.json"

    @staticmethod
    def validate_endpoint_kwargs(**kwargs):
        """
        Validates any verifiable kwarg arguments
        @param kwargs: key-value argument to validate
        @return: bool
        """
        endpoint_kwargs = {k: v for k, v in kwargs.items() if k in _VERIFIABLE_ARGS_MAP.keys()}
        for key, val in endpoint_kwargs.items():
            validation_func = _VERIFIABLE_ARGS_MAP[key]
            validation_func(val)
        return True


_VERIFIABLE_ARGS_MAP = {
    "CIK": CIKOpts.validate_cik_arg,
    "PERIOD_FORMAT": PeriodFormatOpts.validate_period_format_arg
}
