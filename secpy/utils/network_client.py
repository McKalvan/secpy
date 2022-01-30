import backoff
import requests
from ratelimiter import RateLimiter
from enum import Enum
from tqdm import tqdm


class NetworkClient:
    def __init__(self,
                 user_agent,
                 rate_limit=10,
                 max_retries=5
                 ):
        self._headers = self.__set_headers(user_agent)
        self._rate_limit = self.__set_rate_limit(rate_limit)
        self.max_retries = self.__set_max_retries(max_retries)

    @staticmethod
    def __set_headers(user_agent):
        assert isinstance(user_agent, str), "user_agent arg {} is not of type string!".format(user_agent)
        assert user_agent != "" "user_agent must be a non-empty string!"
        return {
            "User-Agent": user_agent
        }

    @staticmethod
    def __set_rate_limit(rate_limit):
        assert isinstance(rate_limit, int) and rate_limit > 0, "rate_limit arg {} must be a positive integer!".format(rate_limit)
        return rate_limit

    @staticmethod
    def __set_max_retries(max_retries):
        assert isinstance(max_retries, int) and max_retries > 0, "rate_limit arg {} must be a positive integer!".format(max_retries)
        return max_retries

    def make_request_json(self, endpoint, **kwargs):
        return self.make_request(endpoint, **kwargs).json()

    def make_request(self, endpoint, **kwargs):
        assert isinstance(endpoint, EndpointEnum), "{} is not of type EndpointEnum!".format(endpoint)

        @RateLimiter(max_calls=self._rate_limit, period=1)
        @backoff.on_exception(backoff.expo,
                              requests.exceptions.RequestException,
                              max_tries=self.max_retries
                              )
        def __make_requests_helper():
            formatted_endpoint = endpoint.value.format(**kwargs)
            return requests.get(
                    formatted_endpoint,
                    headers=self._headers
            )

        response = __make_requests_helper()
        self.__validate_response(response)
        return response

    def download_file(self, endpoint, file_path, chunk_size=128, **kwargs):
        @RateLimiter(max_calls=self._rate_limit, period=1)
        @backoff.on_exception(backoff.expo,
                              requests.exceptions.RequestException,
                              max_tries=self.max_retries
                              )
        def __download_file_helper():
            formatted_endpoint = endpoint.value.format(**kwargs)
            response = requests.get(formatted_endpoint, stream=True, allow_redirects=True, headers=self._headers)
            content_length = int(response.headers.get('content-length'))
            initial_pos = 0
            with open(file_path, "wb") as file:
                with tqdm(total=content_length, unit_scale=True, unit="B", desc=file_path, initial=initial_pos, ascii=True) as pbar:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        file.write(chunk)
                        pbar.update(len(chunk))
        __download_file_helper()


    def __validate_response(self, response):
        pass


class EndpointEnum(Enum):
    __BASE_SEC_URL = "https://www.sec.gov"
    __BASE_DATA_SEC_URL = "https://data.sec.gov"

    COMPANY_TICKER_EXCHANGE = __BASE_SEC_URL + "/files/company_tickers_exchange.json"
    BULK_COMPANY_FACTS = __BASE_SEC_URL + "/Archives/edgar/daily-index/xbrl/companyfacts.zip"
    BULK_SUBMISSIONS = __BASE_SEC_URL + "/Archives/edgar/daily-index/bulkdata/submissions.zip"

    SUBMISSIONS = __BASE_DATA_SEC_URL + "/submissions/CIK{CIK_NUM}.json"
    COMPANY_CONCEPTS = __BASE_DATA_SEC_URL + "/api/xbrl/companyconcepts/CIK{CIK_NUM}/{CONCEPT}.json"
    COMPANY_FACTS = __BASE_DATA_SEC_URL + "/api/xbrl/companyfacts/CIK{CIK_NUM}.json"
    FRAMES = __BASE_DATA_SEC_URL + "/api/xbrl/frames/{STANDARD}/{CONCEPT}/{PERIOD_FORMAT}.json"
