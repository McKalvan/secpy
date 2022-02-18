from enum import Enum

from secpy.core.endpoint_enum import EndpointEnum
from secpy.core.mixins.base_data_object_mixin import BaseDataObjectMixin
from secpy.core.mixins.base_endpoint_mixin import BaseEndpointMixin
from secpy.core.utils.period_format_opts import PeriodFormatOpts


class FramesEndpoint(BaseEndpointMixin):
    """
    Handles the downloading and parsing of Frames data from the SEC REST API
    """
    _endpoint = EndpointEnum.FRAMES

    def get_frames(self, taxonomy, concept, unit, period_format, use_instantaneous=False):
        """
        Gets a Frames instance for a given taxonomy, unit, and period
        @param taxonomy: str, taxonomy to retrieve frames for (ie us-gaap, dei)
        @param concept: str, concept to retrieve frames for (ie Assets, AccountsPayableCurrent)
        @param unit: str, unit to retrieve frames for (ie USD, USD_shares
        @param period_format: str or datetime instance, time period to retrieve frames for (ie, CY2022FY, CY2021Q1)
        @param use_instantaneous: bool, use instantaneous frames
        @return: Frames instance
        """
        period_format_arg = PeriodFormatOpts.format_period_format_arg(period_format, use_instantaneous)
        response = self._validate_args_and_make_request(self._endpoint,
                                                        TAXONOMY=taxonomy,
                                                        CONCEPT=concept,
                                                        UNIT=unit,
                                                        PERIOD_FORMAT=period_format_arg
                                                        )
        return Frames(response)


class Frames(BaseDataObjectMixin):
    class FramesSchemaEnum(Enum):
        TAXONOMY = "taxonomy"
        TAG = "tag"
        CCP = "ccp"
        UOM = "uom"
        LABEL = "label"
        DESCRIPTION = "description"
        PTS = "pts"
        DATA = "data"

    def __init__(self, data):
        """
        Aggregate of CompanyFrames that represents data for a particular taxonomy/concept/unit for all available companies
        at a specified period of time.
        @param data: dict
        """
        self.taxonomy = data[self.FramesSchemaEnum.TAXONOMY.value]
        self.tag = data[self.FramesSchemaEnum.TAG.value]
        self.ccp = data[self.FramesSchemaEnum.CCP.value]
        self.uom = data[self.FramesSchemaEnum.UOM.value]
        self.label = data[self.FramesSchemaEnum.LABEL.value]
        self.description = data[self.FramesSchemaEnum.DESCRIPTION.value]
        self.pts = data[self.FramesSchemaEnum.PTS.value]
        self.data = self.__set_company_frames(data)

    def __set_company_frames(self, data):
        company_frames_arr = data[self.FramesSchemaEnum.DATA.value]
        return [CompanyFrame(obj) for obj in company_frames_arr]


class CompanyFrame(BaseDataObjectMixin):
    class CompanyFrameSchemaEnum(Enum):
        ACCN = "accn"
        CIK = "cik"
        ENTITY_NAME = "entityName"
        LOC = "loc"
        END = "end"
        VAL = "val"

    def __init__(self, data):
        """
        Represents data for a particular taxonomy/concept/unit for a single company
        @param data: dict
        """
        self.accn = data[self.CompanyFrameSchemaEnum.ACCN.value]
        self.cik = data[self.CompanyFrameSchemaEnum.CIK.value]
        self.entity_name = data[self.CompanyFrameSchemaEnum.ENTITY_NAME.value]
        self.loc = data[self.CompanyFrameSchemaEnum.LOC.value]
        self.end = data[self.CompanyFrameSchemaEnum.END.value]
        self.val = data[self.CompanyFrameSchemaEnum.VAL.value]
