import unittest

from secpy.core.utils.cik_opts import CIKOpts


class CIKOptsTest(unittest.TestCase):
    def test_valid_cik_arg_on_valid_ciks(self):
        cik1 = "0000012345"
        cik2 = "1000012349"
        cik3 = "0021923012"
        cik4 = "0000000001"
        ciks = [cik1, cik2, cik3, cik4]
        for cik in ciks:
            self.assertTrue(CIKOpts.validate_cik_arg(cik))

    def test_valid_cik_arg_on_invalid_args(self):
        ticker = "BLH"
        non_numeric = "a000013423"
        invalid_length = "0001234"
        invalid_ciks = [ticker, non_numeric, invalid_length]
        for invalid_cik in invalid_ciks:
            self.assertRaises(AssertionError, CIKOpts.validate_cik_arg, invalid_cik)

    def test_format_cik_int(self):
        cik_int = 12345
        formatted_cik = CIKOpts.format_cik(cik_int)
        expected_cik = "0000012345"
        self.assertEqual(formatted_cik, expected_cik)

    def test_format_cik_str(self):
        cik_int = "12345"
        formatted_cik = CIKOpts.format_cik(cik_int)
        expected_cik = "0000012345"
        self.assertEqual(formatted_cik, expected_cik)


if __name__ == '__main__':
    unittest.main()
