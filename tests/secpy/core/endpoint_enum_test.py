import unittest

from secpy.core.endpoint_enum import EndpointEnum


class EndpointEnumTest(unittest.TestCase):
    def test_validate_endpoint_kwargs(self):
        kwargs = {"CIK": "0000012345", "PERIOD_FORMAT": "CY2020"}
        self.assertTrue(EndpointEnum.validate_endpoint_kwargs(**kwargs))

    def test_validate_endpoint_kwargs_invalid(self):
        kwargs = {"CIK": "0000012", "PERIOD_FORMAT": "CY2020"}
        self.assertRaises(AssertionError, EndpointEnum.validate_endpoint_kwargs, **kwargs)


if __name__ == '__main__':
    unittest.main()
