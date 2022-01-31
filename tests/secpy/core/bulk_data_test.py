import unittest
import os

from secpy.core.bulk_data import BulkDataFileObject
from tests.testutils.mock_utils import mock_company_tickers_exchange, RESOURCES
from zipfile import ZipFile


company_tickers_exchange = mock_company_tickers_exchange()


class BulkDataFileObjectTest(unittest.TestCase):
    BULK_SUBMISSION_FILE = os.path.join(os.path.dirname(__file__),
                                        "..",
                                        "resources",
                                        "bulk_submissions.zip")

    bulk_data_archive_test_path = os.path.join(RESOURCES, "bulk_submissions.zip")

    def test_bulk_data_file_object_mappings(self):
        bulk_data_file_object = BulkDataFileObject(self.bulk_data_archive_test_path, self.company_tickers_exchange)

        expected_cik_to_filename_map = {'0000001750': 'CIK0000001750.json', '0000001800': 'CIK0000001800.json', '0000001961': 'CIK0000001961.json', '0000002034': 'CIK0000002034.json', '0000002098': 'CIK0000002098.json'}
        self.assertEqual(bulk_data_file_object.get_cik_to_filename_map(), expected_cik_to_filename_map)

        expected_ticker_to_filename_map = {'AIR': 'CIK0000001750.json', 'ABT': 'CIK0000001800.json', 'WDDD': 'CIK0000001961.json', 'ACU': 'CIK0000002098.json'}
        self.assertEqual(bulk_data_file_object.get_ticker_to_filename_map(), expected_ticker_to_filename_map)

        expected_unlisted_companies = ['0000002034']
        self.assertEqual(bulk_data_file_object.unlisted_companies, expected_unlisted_companies)

    def test_get_filelist(self):
        bulk_data_file_object = BulkDataFileObject(self.bulk_data_archive_test_path, self.company_tickers_exchange)
        actual_files = bulk_data_file_object.get_filelist()
        actual_file_names = [file.filename for file in actual_files]
        expected_files = ZipFile(self.bulk_data_archive_test_path).filelist
        expected_file_names = [file.filename for file in expected_files]

        self.assertListEqual(actual_file_names, expected_file_names)

    def test_archive_exists(self):
        bulk_data_file_object = BulkDataFileObject(self.bulk_data_archive_test_path, self.company_tickers_exchange)
        self.assertTrue(bulk_data_file_object.archive_exists)


if __name__ == '__main__':
    unittest.main()
