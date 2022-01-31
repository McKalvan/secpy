from enum import Enum

from secpy.company_facts import HasFactMixin
from secpy.core.endpoint_enum import EndpointEnum
from secpy.core.mixins.base_endpoint_mixin import BaseEndpointMixin


class CompanyConceptEndpoint(BaseEndpointMixin):
    """
    Handles the downloading and parsing of individual concepts for a given company
    """
    _endpoint = EndpointEnum.COMPANY_CONCEPT

    def get_company_concept_for_ticker(self, ticker, taxonomy, concept):
        cte_object = self._ticker_cte_map.lookup_ticker(ticker)
        return self.get_company_concept_for_cik(cte_object.cik, taxonomy, concept)

    def get_company_concept_for_cik(self, cik, taxonomy, concept):
        response = self._validate_args_and_make_request(self._endpoint, CIK=cik, TAXONOMY=taxonomy, CONCEPT=concept)
        return CompanyConcept(response)


class CompanyConcept(HasFactMixin):
    class CompanyConceptSchema(Enum):
        CIK = "cik"
        TAXONOMY = "taxonomy"
        TAG = "tag"
        LABEL = "label"
        DESCRIPTION = "description"
        ENTITY_NAME = "entityName"
        UNITS = "units"

    def __init__(self, data):
        """
        Container class for CompanyConcept data
        @param data: dict
        """
        super().__init__(data, data[self.CompanyConceptSchema.TAG.value])
        self.cik = data[self.CompanyConceptSchema.CIK.value]
        self.taxonomy = data[self.CompanyConceptSchema.TAXONOMY.value]
        self.label = data.get(self.CompanyConceptSchema.LABEL.value)
        self.description = data.get(self.CompanyConceptSchema.DESCRIPTION.value)
        self.entity_name = data.get(self.CompanyConceptSchema.ENTITY_NAME.value)
