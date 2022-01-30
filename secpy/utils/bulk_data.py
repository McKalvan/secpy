import os
import shutil
from zipfile import ZipFile
from tempfile import gettempdir
import re
import json
from abc import ABC, abstractmethod
import time

from pyedgar.utils.mixins.ticker_cte_map_mixin import TickerCTEMapMixin


class BulkDataEndpoint(TickerCTEMapMixin, ABC):

    def __init__(self, existing_archive=None, **kwargs):
        super().__init__(**kwargs)
        self._archive_persisted = existing_archive is not None
        self.bulk_data_file_object = self.__set_bulk_data_file_object(existing_archive)

        self._endpoint = None

    def __set_bulk_data_file_object(self, existing_archive):
        return BulkDataFileObject(existing_archive, self._ticker_cte_map) if existing_archive else None

    def download_bulk_data(self, override=True, **kwargs):
        if not self._archive_persisted or (self._archive_persisted and override):
            archive_path = self.__get_temp_zip_file()
            self._network_client.download_file(self._endpoint, archive_path, **kwargs)
            self.bulk_data_file_object = BulkDataFileObject(archive_path, self._ticker_cte_map)
        else:
            self._logger.info("Archive already exists, skipping download...")
        return self

    @staticmethod
    def __get_temp_zip_file():
        temp_dir = gettempdir()
        filename = str(int(time.time()))
        return os.path.join(temp_dir, filename) + ".zip"

    def get_data_from_archive(self, ticker, **kwargs):
        self._get_bulk_data_if_none(**kwargs)
        data = self.bulk_data_file_object.get_json_from_for_ticker_from_zip(ticker)
        return self._parse_data(data)

    def persist_data_file_object(self, output_path):
        if self._archive_persisted:
            raise Exception("Archive at path {} has already been persisted!".format(self.bulk_data_file_object.archive_path))

        if self.bulk_data_file_object.bulk_data_file_exists():
            shutil.move(self.bulk_data_file_object.archive_path, output_path)
            self.__set_bulk_data_file_object(output_path)
            self._archive_persisted = True
        else:
            raise Exception("Bulk data not loaded into memory, nothing to save!")

    def _get_bulk_data_if_none(self, **kwargs):
        if not self.bulk_data_file_object:
            self.download_bulk_data(**kwargs)

    def for_all_companies(self, func):
        return func(self.__extract_file_and_parse_data(filename) for filename in self.bulk_data_file_object.get_filenames())

    def __extract_file_and_parse_data(self, filename):
        data = self.bulk_data_file_object.get_file(filename)
        return self._parse_data(data)

    @abstractmethod
    def _parse_data(self, data):
        pass


class BulkDataFileObject:
    __FILENAME_REGEX = re.compile("CIK\d{10}.json$")

    def __init__(self, archive_path, ticker_cte_map):
        self.archive_path = archive_path
        self.__zipfile = self.__set_zip_file(archive_path)
        self.__ticker_to_filename_map = {}
        self.__cik_to_filename_map = {}
        self.unlisted_companies = []

        self.__create_filename_maps(ticker_cte_map)

    @staticmethod
    def __set_zip_file(archive_path):
        assert os.path.exists(archive_path)
        return ZipFile(archive_path)

    def __create_filename_maps(self, ticker_cte_map):
        # TODO: Some CIKs may have multiple files for a given zip file, EX: CIK0000001750-submissions-001 in bulk submissions
        # These files seem to hold data going back farther in history, but still unclear as the schema of these files is different
        # We are filtering these "duplicate" CIK files out for now but further investigation should be done here
        file_list = self.__zipfile.filelist
        valid_file_list = list(filter(lambda file: self.__filename_matches_pattern(file.filename), file_list))
        valid_file_names = [file.filename for file in valid_file_list]
        for filename in valid_file_names:
            cik = self.__parse_cik_from_filename(filename)
            ticker = ticker_cte_map.lookup_cik(cik)
            if ticker == ticker_cte_map.UNKNOWN:
                self.insert_to_cik_to_filename_map(cik, filename)
                self.insert_to_unlisted_ciks(cik)
            else:
                self.insert_to_cik_to_filename_map(cik, filename)
                self.insert_to_ticker_to_filename_map(ticker.ticker, filename)

    @staticmethod
    def __parse_cik_from_filename(filename):
        return "".join(re.findall('\d+', filename))

    def __filename_matches_pattern(self, filename):
        return bool(self.__FILENAME_REGEX.match(filename))

    def insert_to_ticker_to_filename_map(self, ticker, filename):
        self.__ticker_to_filename_map[ticker] = filename

    def insert_to_cik_to_filename_map(self, cik, filename):
        self.__cik_to_filename_map[cik] = filename

    def insert_to_unlisted_ciks(self, cik):
        self.unlisted_companies.append(cik)

    def get_filename_from_ticker(self, ticker):
        return self.__ticker_to_filename_map[ticker]

    def get_filename_from_cik(self, cik):
        return self.__cik_to_filename_map[cik]

    def get_file(self, filename):
        return json.loads(self.__zipfile.read(filename))

    def get_filenames(self):
        return self.__zipfile.filelist

    def get_json_from_for_ticker_from_zip(self, ticker):
        filename = self.get_filename_from_ticker(ticker)
        return json.loads(self.__zipfile.read(filename))

    def get_json_for_cik_from_zip(self, cik):
        filename = self.get_filename_from_cik(cik)
        return json.loads(self.__zipfile.read(filename))

    def bulk_data_file_exists(self):
        return os.path.exists(self.archive_path)
