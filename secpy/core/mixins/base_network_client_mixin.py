from os import path

from secpy.core.endpoint_enum import EndpointEnum
from secpy.core.network_client import NetworkClient


class BaseNetworkClientMixin:
    def __init__(self, user_agent, **kwargs):
        """
        Mixin for for adding network_client to a class
        @param user_agent: email address to use in headers when making requests to SEC REST API
        @param kwargs:
        """
        self.__network_client = NetworkClient(user_agent, **kwargs)

    def _validate_args_and_make_request(self, endpoint, **kwargs):
        assert EndpointEnum.validate_endpoint_kwargs(**kwargs)
        return self.__network_client.make_request_json(endpoint, **kwargs)

    def _validate_path_and_download_file(self, endpoint, target_path, **kwargs):
        assert not path.exists(target_path), "target_path {} already exists!".format(target_path)
        return self.__network_client.download_file(endpoint, target_path, **kwargs)
