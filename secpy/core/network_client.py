import backoff
import requests
from ratelimiter import RateLimiter
from tqdm import tqdm


class NetworkClient:
    __MAXIMUM_REQUESTS_PER_SEC_CAP = 10

    def __init__(self,
                 user_agent,
                 max_requests_per_sec=10,
                 max_retries=5
                 ):
        """
        Handles all requests to SEC REST API endpoints. Ensures that requests are formatted properly and are in accordance
        with the SEC's recommendations as specified here: https://www.sec.gov/privacy.htm#security
        @param user_agent: Used in header of request to identify application making the request
        @param max_requests_per_sec: Maximum number of request against the SEC REST API in one second
        @param max_retries: Maximum number of retries to make a request before giving up
        """
        self._headers = self.__set_headers(user_agent)
        self._max_requests_per_sec = self.__set_max_requests_per_sec(max_requests_per_sec)
        self.max_retries = self.__set_max_retries(max_retries)

    @staticmethod
    def __set_headers(user_agent):
        assert isinstance(user_agent, str), "user_agent arg {} is not of type string!".format(user_agent)
        assert user_agent != "", "user_agent must be a non-empty string!"
        return {
            "User-Agent": user_agent
        }

    def __set_max_requests_per_sec(self, max_requests_per_sec):
        assert isinstance(max_requests_per_sec, int) and max_requests_per_sec > 0, "max_requests_per_sec arg {} must be a positive integer!".format( max_requests_per_sec)
        assert max_requests_per_sec <= self.__MAXIMUM_REQUESTS_PER_SEC_CAP, "max_requests_per_sec {} must be less than or equal to {} or else application risks getting rate limited. " \
                                                                            "See https://www.sec.gov/privacy.htm#security for more information re. rate limiting".format(max_requests_per_sec, self.__MAXIMUM_REQUESTS_PER_SEC_CAP)
        return max_requests_per_sec

    @staticmethod
    def __set_max_retries(max_retries):
        assert isinstance(max_retries, int) and max_retries > 0, "rate_limit arg {} must be a positive integer!".format(
            max_retries)
        return max_retries

    def make_request_json(self, endpoint, **kwargs):
        """
        Makes a request to a given endpoint
        @param endpoint: EndpointEnum value
        @param kwargs: used to specify substitution variables in order to format endpoint
        @return: response in json form
        """
        return self.make_request(endpoint, **kwargs).json()

    def make_request(self, endpoint, **kwargs):
        """
        Makes a request to a given SEC REST API endpoint in the set of endpoint templates defined by EndpointEnum
        @param endpoint: EndpointEnum value
        @param kwargs: used to specify substitution variables in order to format endpoint
        @return: response
        """

        @RateLimiter(max_calls=self._max_requests_per_sec, period=1)
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

    def download_file(self, endpoint, file_path, chunk_size, disable_progress_bar=False, **kwargs):
        """
        Downloads a file from the SEC REST API and stores it on disk
        @param disable_progress_bar: bool, disables the progress bar from being logged
        @param endpoint: EndpointEnum value
        @param file_path: output location of the file
        @param chunk_size: number of bytes to read into memory while iterating over response
        @param kwargs: used to specify substitution variables in order to format endpoint
        @return:
        """
        @RateLimiter(max_calls=self._max_requests_per_sec, period=1)
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
                with tqdm(total=content_length, unit_scale=True, unit="B", desc=file_path, initial=initial_pos, ascii=True, disable=disable_progress_bar) as pbar:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        file.write(chunk)
                        pbar.update(len(chunk))

        __download_file_helper()

    @staticmethod
    def __validate_response(response):
        response.raise_for_status()
