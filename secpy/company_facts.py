from enum import Enum
from datetime import datetime

from secpy.core.bulk_data import BulkDataEndpoint
from secpy.core.endpoint_enum import EndpointEnum
from secpy.core.mixins.base_data_object_mixin import BaseDataObjectMixin
from secpy.core.mixins.base_endpoint_mixin import BaseEndpointMixin
from types import SimpleNamespace

from secpy.core.utils.cik_opts import CIKOpts


class CompanyFactsEndpoint(BaseEndpointMixin):
    """
    Handles the downloading and parsing of all company concepts of a given company.
    """
    _endpoint = EndpointEnum.COMPANY_FACTS

    def get_company_facts_for_ticker(self, ticker):
        cte_object = self._ticker_cte_map.lookup_ticker(ticker)
        return self.get_company_facts_for_cik(cte_object.cik)

    def get_company_facts_for_cik(self, cik):
        response = self._validate_args_and_make_request(self._endpoint, CIK=cik)
        return CompanyFacts(response)


class CompanyFactsBulkEndpoint(BulkDataEndpoint):
    """
    Handles the downloading and parsing of the bulk CompanyFacts zip file
    """
    _endpoint = EndpointEnum.BULK_COMPANY_FACTS

    def _parse_data(self, data):
        return CompanyFacts(data)


class CompanyFacts(BaseDataObjectMixin):
    class CompanyFactsSchemaEnum(Enum):
        CIK = "cik"
        ENTITY_NAME = "entityName"
        FACTS = "facts"

    def __init__(self, data):
        """
        Container class for company facts data.
        Data is divided between one or more accounting standards (AKA taxonomies) and then is further broken down into the individual
        concepts that describe various components of reported financial data for a given company.
        Each concept contains an array of data where each element represents the value of that fact for a given filing
        @param data: dict
        """
        self.cik = self.__set_cik(data)
        self.entity_name = data.get(self.CompanyFactsSchemaEnum.ENTITY_NAME.value)
        self.taxonomies = self.__parse_taxonomies(data)

    def __set_cik(self, data):
        cik = data.get(self.CompanyFactsSchemaEnum.CIK.value, 0)
        return CIKOpts.format_cik(cik)

    def __parse_taxonomies(self, data):
        return SimpleNamespace(**{
            taxonomy_name.replace("-", "_"): SimpleNamespace(**{
                concept_name:  Concept(concept_value, concept_name) for concept_name, concept_value in taxonomy_concepts.items()
            })
            for taxonomy_name, taxonomy_concepts in data.get(self.CompanyFactsSchemaEnum.FACTS.value, {}).items()
        })

    def list_taxonomies(self):
        return list(self.taxonomies.__dict__.keys())

    def get_taxonomy(self, taxonomy):
        return self.taxonomies.__dict__[taxonomy]

    def get_concept(self, taxonomy, fact):
        taxonomy_data = self.get_taxonomy(taxonomy)
        return taxonomy_data.__dict__[fact]

    def get_statement_history(self):
        """
        Groups facts together by the form type, financial year, and financial period to form a Statement instance
        @return: List[Statement]
        """
        filing_map = {}
        for concepts in self.taxonomies.__dict__.values():
            for concept_name, concept in concepts.__dict__.items():
                form_period_unit_map = self.__get_form_period_map_for_concept(concept)
                for form_period, facts in form_period_unit_map.items():
                    if form_period not in filing_map:
                        filing_map[form_period] = Statement(facts)
                    else:
                        existing_filing_map = filing_map[form_period]
                        existing_filing_map.add_fact_to_map(concept_name, facts)
        return StatementHistory(filing_map)

    @staticmethod
    def __get_form_period_map_for_concept(concept):
        form_period_unit_map = {}
        for unit_name, facts in concept.units.__dict__.items():
            for fact in facts:
                form_period = fact.get_form_frame()
                if form_period not in form_period_unit_map:
                    form_period_unit_map[form_period] = {unit_name: fact}
                else:
                    existing_form_period_unit_mapping = form_period_unit_map[form_period]
                    existing_form_period_unit_mapping[unit_name] = fact
        return form_period_unit_map


class StatementHistory(BaseDataObjectMixin):
    def __init__(self, form_period_filing_map):
        self.__form_period_filing_map = form_period_filing_map

    def get_all_statements(self):
        """
        Gets all statements in StatementHistory
        @return: List[Statements]
        """
        return list(self.__form_period_filing_map.values())

    def get_statement_for_form_and_period(self, form, period):
        """
        Gets a Statement instance for a particular form and period if it exists
        @param form: str
        @param period: str
        @return: Statement
        """
        key = "{}_{}".format(form, period)
        return self.__form_period_filing_map[key]

    def get_statements_for_form(self, form):
        """
        Gets all statements for a particular form type
        @param form: str
        @return: List[Statement]
        """
        return [statement for key, statement in self.__form_period_filing_map.items() if key.startswith(form)]

    def get_statements_for_date_range(self, start_date=None, end_date=None, date_format="%y/%m/%d"):
        """
        Gets all statements that were filed w/in a given date range.
        If start_date but not end_date is specified, all statements filed after start_date will be returned
        If end_date but not start_date is specified, all statements filed before end_date will be returned
        @param start_date: str or datetime instance
        @param end_date: str or datetime instance
        @param date_format: str, the date format of any string start_time/end_time args
        @return: List[Statement]
        """
        assert start_date or end_date, "At least one of start_date or end_date arguments must be populated!"
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, date_format)
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, date_format)
        if start_date and end_date:
            assert start_date < end_date, "start_date cannot be greater than end_date!"

        result = []
        for statement in self.__form_period_filing_map.values():
            statement_filed_date = datetime.strptime(statement.filed, "%Y-%m-%d")
            if start_date and end_date and start_date < statement_filed_date < end_date:
                result.append(statement)
                continue
            if start_date and not end_date and statement_filed_date > start_date:
                result.append(statement)
            if end_date and not start_date and statement_filed_date < end_date:
                result.append(statement)
        return result


class Statement(BaseDataObjectMixin):
    def __init__(self, facts):
        """
        Contains an aggregation of all facts available for a company for a particular form type, fiscal year, and fiscal period
        @facts: Initial Unit -> Fact map instance to initialize object attributes
        """
        fact = facts[list(facts.keys())[0]]
        self.start = fact.start
        self.end = fact.end
        self.accn = fact.accn
        self.fiscal_year = fact.fiscal_year
        self.fiscal_period = fact.fiscal_period
        self.form = fact.form
        self.filed = fact.filed
        self.__facts_map = self.__initialize_facts_map(facts, fact.concept_name)

    @staticmethod
    def __initialize_facts_map(facts, concept_name):
        return {concept_name: facts}

    def add_fact_to_map(self, fact_name, unit_to_val_map):
        self.__facts_map[fact_name] = unit_to_val_map

    def get_facts_for_unit(self, fact_name, unit):
        return self.__facts_map[fact_name][unit]

    def list_all_facts(self):
        return self.__facts_map.keys()

    def get_all_facts(self):
        """
        Returns all facts for the given Statement
        @return: dict, map of fact -> unit
        """
        return self.__facts_map


class HasFactMixin(BaseDataObjectMixin):
    UNITS = "units"

    def __init__(self, data, tag):
        self.tag = tag
        self.units = self.__parse_units(data)

    def __parse_units(self, data):
        return SimpleNamespace(**{
            unit_name.replace("/", "_"): [Fact(fact_data, self.tag, unit_name) for fact_data in unit_value]
            for unit_name, unit_value in data[self.UNITS].items()
        })

    def get_unit(self, key):
        return self.units.__dict__[key]

    def list_units(self):
        return list(self.units.__dict__.keys())


class Concept(HasFactMixin):
    class ConceptSchemaEnum(Enum):
        LABEL = "label"
        DESCRIPTION = "description"
        UNITS = "units"

    def __init__(self, data, concept_name):
        """
        Represents a single financial concept for a particular company (Ex. AccountsPayable, AccountsReceivable, etc)
        The measurement of a concept is broken down by units (Ex. USD, USD/share, shares, etc) which are parsed into Fact instances
        @param data: dict
        """
        super().__init__(data, concept_name)
        self.label = data.get(self.ConceptSchemaEnum.LABEL.value)
        self.description = data.get(self.ConceptSchemaEnum.DESCRIPTION.value)


class Fact(BaseDataObjectMixin):
    class FactSchemaEnum(Enum):
        START = "start"
        END = "end"
        VAL = "val"
        ACCN = "accn"
        FY = "fy"
        FP = "fp"
        FORM = "form"
        FILED = "filed"
        FRAME = "frame"

    def __init__(self, data, concept_name, unit):
        """
        Represents the state of a single concept for a given company as measured by some unit at a given time for some form type
        @param data: dict
        """
        self.concept_name = concept_name
        self.unit = unit
        self.start = data.get(self.FactSchemaEnum.START.value)
        self.end = data[self.FactSchemaEnum.END.value]
        self.value = data[self.FactSchemaEnum.VAL.value]
        self.accn = data[self.FactSchemaEnum.ACCN.value]
        self.fiscal_year = data[self.FactSchemaEnum.FY.value]
        self.fiscal_period = data[self.FactSchemaEnum.FP.value]
        self.form = data[self.FactSchemaEnum.FORM.value]
        self.filed = data[self.FactSchemaEnum.FILED.value]
        self.frame = data.get(self.FactSchemaEnum.FRAME.value)

    def get_form_frame(self):
        """
        Formats a string in form_fy_fp format where form represents the form type, fy represents financial year, and
        fp represents the financial period in which the form was submitted
        @return: str
        """
        frame = self.frame or "CY{}{}".format(self.fiscal_year, self.fiscal_period)
        return "{}_{}".format(self.form, frame)
