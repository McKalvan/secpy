from enum import Enum

from secpy.core.bulk_data import BulkDataEndpoint
from secpy.core.endpoint_enum import EndpointEnum
from secpy.core.mixins.base_data_object_mixin import BaseDataObjectMixin
from secpy.core.mixins.base_endpoint_mixin import BaseEndpointMixin
from secpy.core.network_client import NetworkClient
from secpy.core.utils.cik_opts import CIKOpts


class SubmissionsEndpoint(BaseEndpointMixin):
    """
    Handles the downloading and parsing of Submissions data from the SEC REST API
    """
    _endpoint = EndpointEnum.SUBMISSIONS_CIK

    def get_submissions_for_ticker(self, ticker):
        """
        Request submissions data from SEC REST API for a given ticker. Converts ticker -> CIK and then makes request
        @param ticker: str
        @return: Submissions
        """
        cte_object = self._ticker_cte_map.lookup_ticker(ticker)
        return self.get_submission_for_cik(cte_object.cik)

    def get_submission_for_cik(self, cik):
        """
        Request submissions data from SEC REST API for a given CIK.
        @param cik: str
        @return: Submissions
        """
        response = self._validate_args_and_make_request(self._endpoint, CIK=cik)
        return Submissions(response)


class SubmissionsBulkEndpoint(BulkDataEndpoint):
    """
    Handles the downloading and parsing of the bulk Submissions zip file
    """
    _endpoint = EndpointEnum.BULK_SUBMISSIONS

    def _parse_data(self, data):
        return Submissions(data)


class Submissions(BaseDataObjectMixin):
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
        """
        Container class for data retrieved from Submissions endpoint for a given company.
        Includes various metadata on the company and a list of filings made by the company
        @param data: dict
        """
        self.cik = CIKOpts.format_cik(data[self.SubmissionsSchemaEnum.CIK.value])
        self.entity_type = data[self.SubmissionsSchemaEnum.ENTITY_TYPE.value]
        self.sic = data[self.SubmissionsSchemaEnum.SIC.value]
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
        self.addresses = self.__set_addresses(data)
        self.phone = data[self.SubmissionsSchemaEnum.PHONE.value]
        self.flags = data[self.SubmissionsSchemaEnum.FLAGS.value]
        self.former_names = data[self.SubmissionsSchemaEnum.FORMER_NAMES.value]
        self.filings = self.__set_filings(data)

    def __set_addresses(self, data):
        addresses = data[self.SubmissionsSchemaEnum.ADDRESSES.value]
        return {k: Address(v) for k, v in addresses.items()}

    def __set_filings(self, data):
        filings = data[self.SubmissionsSchemaEnum.FILINGS.value]
        return Filings(filings, self.cik)


class Address(BaseDataObjectMixin):
    class AddressesSchemaEnum(Enum):
        STREET_1 = "street1"
        STREET_2 = "street2"
        CITY = "city"
        STATE_OR_COUNTRY = "stateOrCountry"
        STATE_OR_COUNTRY_DESCRIPTION = "stateOrCountryDescription"
        ZIP_CODE = "zipCode"

    def __init__(self, data):
        """
        Represents primary address(es) of a given company based on their filings
        @param data: dict
        """
        self.street_1 = data[self.AddressesSchemaEnum.STREET_1.value]
        self.street_2 = data[self.AddressesSchemaEnum.STREET_2.value]
        self.city = data[self.AddressesSchemaEnum.CITY.value]
        self.state_or_country = data[self.AddressesSchemaEnum.STATE_OR_COUNTRY.value]
        self.state_or_country_description = data[self.AddressesSchemaEnum.STATE_OR_COUNTRY_DESCRIPTION.value]
        self.zip_code = data[self.AddressesSchemaEnum.ZIP_CODE.value]


class HasFilingsMixin(BaseDataObjectMixin):
    def __init__(self, cik):
        self.cik = cik

    def _parse_filings(self, data):
        """
        The 'recent' field returned submissions api endpoint is an object consisting of numerous arrays
        each containing a single element of an overall filing object. The fields of a filing can be stitched together by
        grabbing the i'th index of each field, putting it in a dict keyed by the fieldnames and then passing that dict to a Filing object
        @param data: dict
        @return: List[Filing]
        """
        first_key = list(data.keys())[0]
        num_filings = len(data[first_key])
        return [Filing({k: v[i] for k, v in data.items()}, self.cik) for i in range(num_filings)]


class Filings(HasFilingsMixin):
    class FilingsSchemaEnum(Enum):
        RECENT = "recent"
        FILES = "files"

    def __init__(self, data, cik):
        """
        Represents historical/recent filings for a given company
        @param data: dict
        @param cik: str
        """
        super().__init__(cik)
        self.cik = cik
        self.recent_files = self.__set_recent_filings(data)
        self.historical_files = self.__set_historical_filings(data)

    def __set_recent_filings(self, data):
        recent_filings = data[Filings.FilingsSchemaEnum.RECENT.value]
        return self._parse_filings(recent_filings)

    def __set_historical_filings(self, data):
        historical_files = data[self.FilingsSchemaEnum.FILES.value]
        return [HistoricalFiling(historical_file, self.cik) for historical_file in historical_files]

    def filter_by_form(self, form_type):
        """
        Filter available recent filings by a particular form type
        @param form_type: str
        @return: List[Filing]
        """
        return [form for form in self.recent_files if form.form == form_type]


class HistoricalFiling(HasFilingsMixin):
    class Filing(Enum):
        NAME = "name"
        FILING_COUNT = "filingCount"
        FILING_FROM = "filingFrom"
        FILING_TO = "filingTo"

    def __init__(self, data, cik):
        """
        Per the SEC REST API documentation:
            "The object’s property path contains at least one year’s of filing or to 1,000 (whichever is more) of the most
             recent filings in a compact columnar data array. If the entity has additional filings,
             files will contain an array of additional JSON files and the date range for the filings each one contains."
        This represents the array of additional JSON files that represent excess filings not represented in the initial submissions request
        Specifies the date range covered by a particular set of historical filings and allows for downloading/parsing the additional JSON files
        as Filings instances
        @param data: dict
        @param cik: str, cik associated w/ company
        """
        super().__init__(cik)
        self.cik = cik
        self.filename = data[self.Filing.NAME.value]
        self.filing_count = data[self.Filing.FILING_COUNT.value]
        self.filing_from = data[self.Filing.FILING_FROM.value]
        self.filing_to = data[self.Filing.FILING_TO.value]
        self.file_link = self.__set_file_path()

    def __set_file_path(self):
        return EndpointEnum.SUBMISSIONS.value.format(FILE_NAME=self.filename)

    def get_historical_filings(self, user_agent):
        """
        Makes request to download historical filings data from self.file_link
        @param user_agent: str, used in header of request to identify application making the request
        @return: List[Submission]
        """
        nwc = NetworkClient(user_agent)
        response = nwc.make_request_json(EndpointEnum.SUBMISSIONS, FILE_NAME=self.filename)
        return self._parse_filings(response)


class Filing:
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

    def __init__(self, data, cik):
        """
        Represents a single filing made by a given company.
        Provides various metadata regarding the filing and means w/ which to download the filing
        @param data: dict
        @param cik: cik of the specified company
        """
        self.cik = cik
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
        self.primary_document_name = data[self.FilingSchemaEnum.PRIMARY_DOCUMENT.value]
        self.primary_document_description = data.get(self.FilingSchemaEnum.PRIMARY_DOCUMENT_DESCRIPTION.value)

        self._endpoint_format_kwargs = self.__set_endpoint_format_kwargs()
        self.primary_document_link = EndpointEnum.EDGAR_DATA_ARCHIVES.value.format(**self._endpoint_format_kwargs)

    def __set_endpoint_format_kwargs(self):
        # drop the leading zeroes from cik since they are not used in the endpoint
        cik_num = int(self.cik)
        formatted_accession_num = self.accession_number.replace("-", "")
        return {
            "CIK_NUM": cik_num,
            "ACCESSION_NUM": formatted_accession_num,
            "FILE_NAME": self.primary_document_name
        }

    def download_primary_document(self, user_agent, output_path, chunk_size=1028):
        """
        Downloads the primary document for the SEC archive
        @param user_agent: str, unique identifier needed to make request
        @param output_path: str, path to save downloaded document to
        @param chunk_size: int, number of bytes to process from request at a time
        @return: None
        """
        # TODO is there a better way of going about this that doesn't involve user supplying a user_agent?
        # Seems sort of clumsy. On paper, one request for a single document shouldn't get rate limited
        nwc = NetworkClient(user_agent)
        nwc.download_file(EndpointEnum.EDGAR_DATA_ARCHIVES, output_path, chunk_size,  **self._endpoint_format_kwargs)
