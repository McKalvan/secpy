from enum import Enum

from pyedgar.utils.bulk_data import BulkDataEndpoint
from pyedgar.utils.mixins.ticker_cte_map_mixin import TickerCTEMapMixin
from pyedgar.utils.mixins.base_mixin import DataObjectView
from pyedgar.utils.network_client import EndpointEnum
from pyedgar.utils.ticker_cte_map import format_cik


class CompanyFactsEndpoint(TickerCTEMapMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_company_facts_from_ticker(self, ticker):
        cte_object = self._ticker_cte_map.lookup_ticker(ticker)
        return self.get_company_facts_from_cik(cte_object.cik)

    def get_company_facts_from_cik(self, cik):
        self._validate_cik(cik)
        response = self._network_client.make_request_json(EndpointEnum.COMPANY_FACTS, CIK_NUM=cik)
        return CompanyFacts(response)


class CompanyFactsBulkEndpoint(BulkDataEndpoint):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._endpoint = EndpointEnum.BULK_COMPANY_FACTS

    def _parse_data(self, data):
        return CompanyFacts(data)


class CompanyFacts(DataObjectView):
    class CompanyFactsSchemaEnum(Enum):
        CIK = "cik"
        ENTITY_NAME = "entityName"
        FACTS = "facts"

    def __init__(self, data):
        super().__init__(data)
        self.cik = format_cik(data[self.CompanyFactsSchemaEnum.CIK.value])
        self.entity_name = data[self.CompanyFactsSchemaEnum.ENTITY_NAME.value]
        self.taxonomies = self.__parse_taxonomies(data)

    def __parse_taxonomies(self, data):
        return DataObjectView(
            {
                taxonomy_name.replace("-", "_"): DataObjectView(
                    {
                        concept_name:  Concept(concept_value) for concept_name, concept_value in taxonomy_concepts.items()
                    }
                )
                for taxonomy_name, taxonomy_concepts in data[self.CompanyFactsSchemaEnum.FACTS.value].items()
            }
        )

    def list_taxonomies(self):
        return self.keys()

    def get_taxonomy(self, taxonomy):
        return self.taxonomies._get(taxonomy)


class Concept(DataObjectView):
    class ConceptSchemaEnum(Enum):
        LABEL = "label"
        DESCRIPTION = "description"
        UNITS = "units"

    def __init__(self, data):
        super().__init__(data)
        self.label = data.get(self.ConceptSchemaEnum.LABEL.value)
        self.description = data.get(self.ConceptSchemaEnum.DESCRIPTION.value)
        self.units = self.__parse_units(data)

    def __parse_units(self, data):
        return DataObjectView(
            {
                    unit_name: [
                        Fact(fact_data) for fact_data in unit_value
                    ] for unit_name, unit_value in data[self.ConceptSchemaEnum.UNITS.value].items()
            }
        )

    def get_unit(self, key):
        return self._get(key)

    def list_units(self):
        return self.keys()


class Fact(DataObjectView):
    class FactSchemaEnum(Enum):
        END = "end"
        VAL = "val"
        ACCN = "accn"
        FY = "fy"
        FP = "fp"
        FORM = "form"
        FILED = "filed"
        FRAME = "frame"

    def __init__(self, data):
        super().__init__(data)
        self.end = data[self.FactSchemaEnum.END.value]
        self.value = data[self.FactSchemaEnum.VAL.value]
        self.accn = data[self.FactSchemaEnum.ACCN.value]
        self.fiscal_year = data[self.FactSchemaEnum.FY.value]
        self.fiscal_period = data[self.FactSchemaEnum.FP.value]
        self.form = data[self.FactSchemaEnum.FORM.value]
        self.filled = data[self.FactSchemaEnum.FILED.value]
        self.frame = data.get(self.FactSchemaEnum.FRAME.value)
