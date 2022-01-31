import re
from datetime import date


class PeriodFormatOpts:

    @staticmethod
    def validate_period_format_arg(period_format_str):
        pf_regex = re.compile("CY\d{4}(Q\dI*)*")
        match = pf_regex.fullmatch(period_format_str)
        assert match is not None, "Invalid period_format argument {}!" \
                                  "Argument should take one of the following forms:" \
                                  "CY####, CY####Q#, or CY####Q#I"
        return True

    @staticmethod
    def format_period_format_arg(period_format, use_instantaneous=False):
        instantaneous_flag = "I" if use_instantaneous else ""
        if isinstance(period_format, str):
            return period_format + instantaneous_flag
        elif isinstance(period_format, date):
            year = period_format.year
            quarter = ((period_format.month - 1) // 3) + 1
            return "CY{}Q{}{}".format(year, quarter, instantaneous_flag)
        elif isinstance(period_format, int):
            return "CY{}".format(period_format)
        else:
            raise Exception("Type of period_format must be either a string or datetime.date: {}".format(period_format))
