
CIK_LENGTH = 10


class CIKOpts:
    @staticmethod
    def validate_cik_arg(cik):
        """
        Validate that a given CIK is valid. A valid CIK is 10-digit numeric value
        @return: bool
        """
        assert cik.isnumeric(), "Input CIK {} is non-numeric!".format(cik)
        assert len(cik) == CIK_LENGTH, "Input CIK {} must be a {} digit number".format(cik, CIK_LENGTH)
        return True

    @staticmethod
    def format_cik(cik):
        """
        Pads given cik_num w/ additional 0s so that the result is a 10 digit numeric string
        @param cik: CIK integer to format
        @return: string, 10 digit numeric string
        """
        formatted_cik = str(cik).zfill(CIK_LENGTH)
        return formatted_cik




