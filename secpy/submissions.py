from enum import Enum

from pyedgar.utils.bulk_data import BulkDataEndpoint
from pyedgar.utils.mixins.base_mixin import DataObjectView
from pyedgar.utils.mixins.ticker_cte_map_mixin import TickerCTEMapMixin
from pyedgar.utils.network_client import EndpointEnum


class SubmissionsEndpoint(TickerCTEMapMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_submissions_from_ticker(self, ticker):
        cte_object = self._ticker_cte_map.lookup_ticker(ticker)
        return self.get_submission_from_cik(cte_object.cik)

    def get_submission_from_cik(self, cik):
        self._validate_cik(cik)
        response = self._network_client.make_request_json(EndpointEnum.SUBMISSIONS, CIK_NUM=cik)
        return Submissions(response)


class SubmissionsBulkEndpoint(BulkDataEndpoint):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._endpoint = EndpointEnum.BULK_SUBMISSIONS

    def _parse_data(self, data):
        return Submissions(data)


class Submissions(DataObjectView):
    class SubmissionsSchemaEnum(Enum):
        CIK = "cik"
        ENTITY_TYPE = "entityType"
        SIC = "sic"
        SIC_DESCRIPTION = "sicDescription"
        INSIDER_TRANSACTION_FOR_OWNER_EXISTS = "insiderTransactionForOwnerExists"
        INSIDER_TRANSACTION_FOR_ISSUER_EXISTS = "insiderTransactionForIssuerExists"
        NAME = "name"
        TICKERS = "tickers"
        EXCHANGES = "exchanges"
        EIN = "ein"
        DESCRIPTION = "description"
        WEBSITE = "website"
        INVESTOR_WEBSITE = "investorWebsite"
        CATEGORY = "category"
        FISCAL_YEAR_END = "fiscalYearEnd"
        STATE_OF_INCORPORATION = "stateOfIncorporation"
        STATE_OF_INCORPORATION_DESCRIPTION = "stateOfIncorporationDescription"
        ADDRESSES = "addresses"
        PHONE = "phone"
        FLAGS = "flags"
        FORMER_NAMES = "formerNames"
        FILINGS = "filings"

    def __init__(self, data):
        super().__init__(data)
        self.cik = data[self.SubmissionsSchemaEnum.CIK.value]
        self.entity_type = data[self.SubmissionsSchemaEnum.ENTITY_TYPE.value]
        self.sic = data[self.SubmissionsSchemaEnum.data]
        self.sic_description = data[self.SubmissionsSchemaEnum.SIC_DESCRIPTION.value]
        self.insider_transaction_for_owner_exists = data[self.SubmissionsSchemaEnum.INSIDER_TRANSACTION_FOR_OWNER_EXISTS.value]
        self.insider_transaction_for_issuer_exists = data[self.SubmissionsSchemaEnum.INSIDER_TRANSACTION_FOR_ISSUER_EXISTS.value]
        self.name = data[self.SubmissionsSchemaEnum.NAME.value]
        self.tickers = data[self.SubmissionsSchemaEnum.TICKERS.value]
        self.exchanges = data[self.SubmissionsSchemaEnum.EXCHANGES.value]
        self.ein = data[self.SubmissionsSchemaEnum.EIN.value]
        self.description = data[self.SubmissionsSchemaEnum.DESCRIPTION.value]
        self.website = data[self.SubmissionsSchemaEnum.WEBSITE.value]
        self.investor_website = data[self.SubmissionsSchemaEnum.INVESTOR_WEBSITE.value]
        self.category = data[self.SubmissionsSchemaEnum.CATEGORY.value]
        self.fiscal_year_end = data[self.SubmissionsSchemaEnum.FISCAL_YEAR_END.value]
        self.state_of_incorporation = data[self.SubmissionsSchemaEnum.STATE_OF_INCORPORATION.value]
        self.state_of_incorporation_description = data[self.SubmissionsSchemaEnum.STATE_OF_INCORPORATION_DESCRIPTION.value]
        self.ADDRESSES = self.__set_addresses(data)
        self.phone = data[self.SubmissionsSchemaEnum.PHONE.value]
        self.flags = data[self.SubmissionsSchemaEnum.FLAGS.value]
        self.former_names = data[self.SubmissionsSchemaEnum.FORMER_NAMES]
        self.filings = self.__set_filings(data)

    def __set_addresses(self, data):
        addresses = data[self.SubmissionsSchemaEnum.ADDRESSES.value]
        return {k: Address(v) for k, v in addresses.items()}

    def __set_filings(self, data):
        filings = data[self.SubmissionsSchemaEnum.FILINGS.value]
        return Filings(filings)


class Address(DataObjectView):
    class AddressesSchemaEnum(Enum):
        STREET_1 = "street1"
        STREET_2 = "street2"
        CITY = "city"
        STATE_OR_COUNTRY = "stateOrCountry"
        STATE_OR_COUNTRY_DESCRIPTION = "stateOrCountryDescription"
        ZIP_CODE = "zipCode"

    def __init__(self, data):
        super().__init__(data)
        self.street_1 = data[self.AddressesSchemaEnum.STREET_1.value]
        self.street_2 = data[self.AddressesSchemaEnum.STREET_2.value]
        self.city = data[self.AddressesSchemaEnum.CITY.value]
        self.state_or_country = data[self.AddressesSchemaEnum.STATE_OR_COUNTRY.value]
        self.state_or_country_description = data[self.AddressesSchemaEnum.STATE_OR_COUNTRY_DESCRIPTION.value]
        self.zip_code = data[self.AddressesSchemaEnum.ZIP_CODE.value]


class Filings(DataObjectView):
    class FilingsSchemaEnum(Enum):
        RECENT = "recent"
        FILES = "files"

    # def __init__(self, data):
    #     super().__init__(data)
    #     self.recent_files = self.__set_recent_filings(data)
    #     self.historical_files = self.__set_historical_filings(data)

    def __set_recent_filings(self, data):
        """
        The 'recent' field returned submissions api endpoint is an object consisting of numerous arrays
        each containing a single element of an overall filing object. The fields of a filing can be stitched together by
        grabbing the i'th index of each field, putting it in a dict keyed by the fieldnames and then passing that dict to a Filing object
        """
        recent_filings = data[self.FilingsSchemaEnum.RECENT.value]
        # The choice of column here is arbitary since they should all have the same length
        num_filings = len(recent_filings[Filing.FilingSchemaEnum.PRIMARY_DOCUMENT])
        return [Filing({k: v[i] for k, v in recent_filings.items()}) for i in range(num_filings)]

    def __set_historical_filings(self, data):
        historical_files = data[self.FilingsSchemaEnum.FILES.value]
        return [HistoricalFiling(historical_file) for historical_file in historical_files]


class Filing(DataObjectView):
    class FilingSchemaEnum(Enum):
        ACCESSION_NUMBER = "accessionNumber"
        FILING_DATE = "filingDate"
        REPORT_DATE = "reportDate"
        ACCEPTANCE_DATE_TIME = "acceptanceDateTime"
        ACT = "act"
        FORM = "form"
        FILE_NUMBER = "fileNumber"
        FILM_NUMBER = "filmNumber"
        ITEMS = "items"
        SIZE = "size"
        IS_XBRL = "isXBRL"
        IS_INLINE_XBRL = "isInlineXBRL"
        PRIMARY_DOCUMENT = "primaryDocument"
        PRIMARY_DOCUMENT_DESCRIPTION = "primaryDocumentDescription"

    def __init__(self, data):
        super().__init__(data)
        self.accession_number = data[self.FilingSchemaEnum.ACCESSION_NUMBER.value]
        self.filing_date = data[self.FilingSchemaEnum.FILING_DATE.value]
        self.report_date = data[self.FilingSchemaEnum.REPORT_DATE.value]
        self.acceptance_date_time = data[self.FilingSchemaEnum.ACCEPTANCE_DATE_TIME.value]
        self.act = data[self.FilingSchemaEnum.ACT.value]
        self.form = data[self.FilingSchemaEnum.FORM.value]
        self.file_number = data[self.FilingSchemaEnum.FILE_NUMBER.value]
        self.film_number = data[self.FilingSchemaEnum.FILM_NUMBER.value]
        self.items = data[self.FilingSchemaEnum.ITEMS.value]
        self.size = data[self.FilingSchemaEnum.SIZE.value]
        self.is_xbrl = data[self.FilingSchemaEnum.IS_XBRL.value]
        self.is_inline_xbrl = data[self.FilingSchemaEnum.IS_INLINE_XBRL.value]
        self.primary_document = data[self.FilingSchemaEnum.PRIMARY_DOCUMENT.value]
        self.primary_document_description = data[self.FilingSchemaEnum.PRIMARY_DOCUMENT_DESCRIPTION.value]


class HistoricalFiling(DataObjectView):
    class Filing(Enum):
        NAME = "NAME"
        FILING_COUNT = "filingCount"
        FILING_FROM = "filingFrom"
        FILING_TO = "filingTo"

    def __init__(self, data):
        super().__init__(data)
