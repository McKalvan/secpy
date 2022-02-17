from abc import ABC, abstractmethod
import os
import shutil
from zipfile import ZipFile
from tempfile import gettempdir
import re
import json
import time

from secpy.core.mixins.base_endpoint_mixin import BaseEndpointMixin


class BulkDataEndpoint(BaseEndpointMixin, ABC):

    def __init__(self, user_agent, existing_archive=None, **kwargs):
        """
        Base class for downloading and parsing SEC bulk ZIP files.
        ZIP files are updated everyday at approximately 3:00 AM (EST)
        @param existing_archive: str, full path to existing archive file to parse instead of downloading new ZIP file from SEC
        @param kwargs:
        """
        super().__init__(user_agent, **kwargs)
        self._archive_persisted = existing_archive is not None
        self.bulk_data_file_object = self.__set_bulk_data_file_object(existing_archive)

    def __set_bulk_data_file_object(self, existing_archive):
        return BulkDataFileObject(existing_archive, self._ticker_cte_map) if existing_archive else None

    def download_bulk_data(self, override=False, chunk_size=1028):
        """
        Download from bulk data endpoint to a temp directory and set the bulk_data_file_object
        @param override: bool, override existing_archive and download
        @param chunk_size: int, number of bytes to read into memory while iterating over response
        @return:
        """
        if not self._archive_persisted or (self._archive_persisted and override):
            archive_path = self.__get_temp_zip_file_path()
            self._validate_path_and_download_file(self._endpoint, archive_path, chunk_size=chunk_size)
            self.bulk_data_file_object = BulkDataFileObject(archive_path, self._ticker_cte_map)
        else:
            self._logger.warn("Archive already exists, skipping download...")
        return self

    @staticmethod
    def __get_temp_zip_file_path():
        temp_dir = gettempdir()
        filename = str(int(time.time()))
        return os.path.join(temp_dir, filename) + ".zip"

    def get_data_for_ticker_from_archive(self, ticker):
        """
        Parses data from the file associated w/ ticker from the zip file. Downloads the zip file if it doesn't exist.
        @param ticker: converted to CIK to find file to parse from archive
        @return:
        """
        self._get_bulk_data_if_none()
        data = self.bulk_data_file_object.get_json_for_ticker_from_zip(ticker)
        return self._parse_data(data)

    def persist_zipfile(self, output_path):
        """
        Persists the bulk data zip file to a non-temporary location specified by output_path
        @param output_path: Full path to persists the bulk data zip file
        @return: None
        """
        if self._archive_persisted:
            raise Exception("Archive at path {} has already been persisted!".format(self.bulk_data_file_object.archive_path))

        if self.bulk_data_file_object.archive_exists():
            shutil.move(self.bulk_data_file_object.archive_path, output_path)
            self.__set_bulk_data_file_object(output_path)
            self._archive_persisted = True
        else:
            raise Exception("Bulk data not loaded into memory, nothing to save!")

    def _get_bulk_data_if_none(self, **kwargs):
        if not self.bulk_data_file_object:
            self.download_bulk_data(**kwargs)

    def for_all_companies(self, func):
        """
        Applies some function to all data in archive, ie min, max, avg of some value
        @param func: python callable, function to apply to entire set of data in archive
        @return: return value of func
        """
        return func(self.__extract_file_and_parse_data(filename) for filename in self.bulk_data_file_object.get_filelist())

    def for_each_company(self, func):
        """
        Applies some function to each data object in the archive
        @param func: python callable, function to apply to each data object
        @return: list of return value of func
        """
        self._get_bulk_data_if_none()
        return [func(self.__extract_file_and_parse_data(filename)) for filename in self.bulk_data_file_object.get_filelist()]

    def __extract_file_and_parse_data(self, filename):
        data = self.bulk_data_file_object.get_file(filename)
        return self._parse_data(data)

    def __del__(self):
        """
        Deletes bulk data zip file from temporary location after object goes out of scope
        @return:
        """
        if not self._archive_persisted and self.bulk_data_file_object and self.bulk_data_file_object.archive_exists():
            os.remove(self.bulk_data_file_object.archive_path)

    @abstractmethod
    def _parse_data(self, data):
        pass


class BulkDataFileObject:
    __FILENAME_REGEX = re.compile("CIK\d{10}.json$")

    def __init__(self, archive_path, ticker_cte_map):
        """
        Handles the parsing of files in bulk data zip file and the creation of CIK/ticker to filename maps.
        @param archive_path: Full path of bulk data zip file
        @param ticker_cte_map: ticker to CTE map object used to create the CIK/Ticker to filename maps
        """
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
        """
        Creates the CIK/ticker -> filename mappings from files in bulk ZIP file
        @param ticker_cte_map: ticker -> CTEObject map. Used to map CIK from filenames -> ticker
        @return:
        """
        file_list = self.__zipfile.filelist
        valid_file_list = list(filter(lambda file: self.__filename_matches_pattern(file.filename), file_list))
        valid_file_names = [file.filename for file in valid_file_list]
        for filename in valid_file_names:
            cik = self.__parse_cik_from_filename(filename)
            ticker = ticker_cte_map.lookup_cik(cik)
            if ticker == ticker_cte_map.UNKNOWN:
                self.__insert_to_cik_to_filename_map(cik, filename)
                self.__insert_to_unlisted_ciks(cik)
            else:
                self.__insert_to_cik_to_filename_map(cik, filename)
                self.__insert_to_ticker_to_filename_map(ticker.ticker, filename)

    @staticmethod
    def __parse_cik_from_filename(filename):
        return "".join(re.findall('\d+', filename))

    def __filename_matches_pattern(self, filename):
        return bool(self.__FILENAME_REGEX.match(filename))

    def __insert_to_ticker_to_filename_map(self, ticker, filename):
        self.__ticker_to_filename_map[ticker] = filename

    def __insert_to_cik_to_filename_map(self, cik, filename):
        self.__cik_to_filename_map[cik] = filename

    def __insert_to_unlisted_ciks(self, cik):
        self.unlisted_companies.append(cik)

    def __get_filename_from_ticker(self, ticker):
        return self.__ticker_to_filename_map[ticker]

    def __get_filename_from_cik(self, cik):
        return self.__cik_to_filename_map[cik]

    def get_file(self, filename):
        return json.loads(self.__zipfile.read(filename))

    def get_filelist(self):
        return self.__zipfile.filelist

    def get_json_for_ticker_from_zip(self, ticker):
        """
        Gets json data from archive for a particular ticker
        @param ticker: str, ticker to extract data for
        @return: dict
        """
        filename = self.__get_filename_from_ticker(ticker)
        return self.get_file(filename)

    def get_json_for_cik_from_zip(self, cik):
        """
        Gets json data from archive for a particular cik
        @param cik: str, cik to extract data for
        @return: dict
        """
        filename = self.__get_filename_from_cik(cik)
        return self.get_file(filename)

    def archive_exists(self):
        """
        Checks to see if the underlying zip archive still exists
        @return: bool
        """
        return os.path.exists(self.archive_path)

    def get_ticker_to_filename_map(self):
        return self.__ticker_to_filename_map

    def get_cik_to_filename_map(self):
        return self.__cik_to_filename_map
