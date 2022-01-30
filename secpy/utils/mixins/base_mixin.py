import logging
import json

from pyedgar.utils.network_client import NetworkClient


class BaseMixin:
    def __init__(self, network_client=None, **kwargs):
        self._network_client = network_client or NetworkClient(**kwargs)
        self._logger = self.__set_up_logger()

    @staticmethod
    def __set_up_logger():
        return logging

    @staticmethod
    def _validate_cik(cik) -> bool:
        assert cik.isnumeric(), "Input CIK {} is non-numeric!".format(cik)
        assert len(cik) == 10, "Input CIK {} must be a 10 digit number".format(cik)
        return True


class DataObjectView(object):
    def __init__(self, data):
        self.__dict__ = self.__set_data(data)

    @staticmethod
    def __set_data(data):
        assert isinstance(data, dict)
        return data

    def _get(self, key):
        return self.__dict__[key]

    def keys(self):
        return self.__dict__.keys()

    def save(self, file_path):
        json.dump(self.__dict__, file_path)
