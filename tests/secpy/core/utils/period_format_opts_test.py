import unittest

from secpy.core.utils.period_format_opts import PeriodFormatOpts
from datetime import date


class PeriodFormatOptsTest(unittest.TestCase):
    def test_validate_period_format_arg_on_valid_args(self):
        year = "CY2022"
        year_and_quarter = "CY2022Q1"
        year_and_quarter_instantaneous = "CY2022Q1I"
        valid_period_formats = [year, year_and_quarter, year_and_quarter_instantaneous]
        for period_format in valid_period_formats:
            self.assertTrue(PeriodFormatOpts.validate_period_format_arg(period_format))

    def test_validate_period_format_arg_on_invalid_args(self):
        cik = "0000012345"
        invalid_year = "CY22"
        invalid_quarter = "CY2022Q01"
        invalid_instantaneous_flag = "CY2022Q1F"
        invalid_period_formats = [cik, invalid_year, invalid_quarter, invalid_instantaneous_flag, invalid_instantaneous_flag]
        for invalid_period_format in invalid_period_formats:
            self.assertRaises(AssertionError, PeriodFormatOpts.validate_period_format_arg, invalid_period_format)

    def test_format_period_format_arg_str(self):
        period_format_str = "CY2022"
        actual_formatted_period = PeriodFormatOpts.format_period_format_arg(period_format_str)
        self.assertEqual(actual_formatted_period, period_format_str)

        actual_formatted_period_instantaneous = PeriodFormatOpts.format_period_format_arg(period_format_str, use_instantaneous=True)
        expected_formatted_period_instantaenous = "CY2022I"
        self.assertEqual(actual_formatted_period_instantaneous, expected_formatted_period_instantaenous)

    def test_format_period_format_arg_date(self):
        test_date_q1 = date(year=2022, month=1, day=1)
        actual_formatted_period_q1 = PeriodFormatOpts.format_period_format_arg(test_date_q1)
        expected_formatted_period_q1 = "CY2022Q1"
        self.assertEqual(actual_formatted_period_q1, expected_formatted_period_q1)

        test_date_q2 = date(year=2022, month=4, day=1)
        actual_formatted_period_q2 = PeriodFormatOpts.format_period_format_arg(test_date_q2)
        expected_formatted_period_2 = "CY2022Q2"
        self.assertEqual(actual_formatted_period_q2, expected_formatted_period_2)

        test_date_q3 = date(year=2022, month=7, day=1)
        actual_formatted_period_q3 = PeriodFormatOpts.format_period_format_arg(test_date_q3)
        expected_formatted_period_q3 = "CY2022Q3"
        self.assertEqual(actual_formatted_period_q3, expected_formatted_period_q3)

        test_date_q4 = date(year=2022, month=10, day=1)
        actual_formatted_period_q4 = PeriodFormatOpts.format_period_format_arg(test_date_q4, use_instantaneous=True)
        expected_formatted_period_q4 = "CY2022Q4I"
        self.assertEqual(actual_formatted_period_q4, expected_formatted_period_q4)

    def test_period_format_arg_int(self):
        test_year = 2022
        actual_period_format = PeriodFormatOpts.format_period_format_arg(test_year)
        expected_period_format = "CY2022"
        self.assertEqual(actual_period_format, expected_period_format)


if __name__ == '__main__':
    unittest.main()
