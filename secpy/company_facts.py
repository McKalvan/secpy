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
        """
        Gets CompanyFacts for a given ticker
        @param ticker: str, ticker to retrieve CompanyFacts for
        @return: CompanyFacts
        """
        cte_object = self._ticker_cte_map.lookup_ticker(ticker)
        return self.get_company_facts_for_cik(cte_object.cik)

    def get_company_facts_for_cik(self, cik):
        """
        Gets CompanyFacts for a given cik
        @param cik: str, cik to retrieve CompanyFacts for
        @return: CompanyFacts
        """
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
        """
        List available taxonomies in current CompanyFacts instance
        @return: List[str]
        """
        return list(self.taxonomies.__dict__.keys())

    def get_taxonomy(self, taxonomy):
        """
        Get a particular taxonomy in the current CompanyFacts instance
        @param taxonomy: str, taxonomy to retrieve
        @return: dict of str -> Concept
        """
        return self.taxonomies.__dict__[taxonomy]

    def get_concept(self, taxonomy, concept):
        """
        Gets a particular Concept w/in a taxonomy of the current CompanyFacts instance
        @param taxonomy: str, name of taxonomy to retrieve (us-gaap, dei, etc)
        @param concept: str, name of concept to retrieve (Assets, AccountsPayableCurrent)
        @return: Concept
        """
        taxonomy_data = self.get_taxonomy(taxonomy)
        return taxonomy_data.__dict__[concept]

    def get_all_concepts(self):
        """
        Gets all concepts in every taxonomy listed under a given CompanyFacts instance
        @return: dict of Concepts
        """
        return {concept_name: concept_value for concept_dict in self.taxonomies.__dict__.values() for concept_name, concept_value in concept_dict.__dict__.items()}

    def get_statement_history(self):
        """
        Groups facts together by the form type, financial year, and financial period to form a Statement instance
        @return: List[Statement]
        """
        return StatementHistory(self.get_all_concepts())


class StatementHistory(BaseDataObjectMixin):
    def __init__(self, concepts):
        self.statements = self.__set_form_period_filing_map(concepts)

    @staticmethod
    def __set_form_period_filing_map(concepts):
        filing_map = {}
        for concept in concepts.values():
            for unit_name in concept.list_units():
                facts = concept.get_unit(unit_name)
                for fact in facts:
                    if fact.accn not in filing_map:
                        filing_map[fact.accn] = {
                            fact.concept_name: {
                                unit_name: [fact]
                            }
                        }
                    else:
                        existing_filing = filing_map[fact.accn]
                        if fact.concept_name not in existing_filing:
                            existing_filing[fact.concept_name] = {unit_name: [fact]}
                        else:
                            existing_fact = existing_filing[fact.concept_name]
                            if unit_name not in existing_fact:
                                existing_fact[unit_name] = [fact]
                            else:
                                existing_unit = existing_fact[unit_name]
                                existing_unit.append(fact)
        return {accn: Statement(fact_list) for accn, fact_list in filing_map.items()}

    def get_all_statements(self):
        """
        Gets all statements in StatementHistory
        @return: List[Statements]
        """
        return list(self.statements.values())

    def get_statement_for_form_and_period(self, form, period):
        """
        Gets a Statement instance for a particular form and period if it exists
        @param form: str
        @param period: str
        @return: Statement
        """
        key = "{}_{}".format(form, period)
        return self.statements[key]

    def get_statements_for_form(self, form):
        """
        Gets all statements for a particular form type
        @param form: str
        @return: List[Statement]
        """
        return [statement for key, statement in self.statements.items() if key.startswith(form)]

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
        for statement in self.statements.values():
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
        fact = list(list(facts.values())[0].values())[0][0]
        self.accn = fact.accn
        self.fiscal_year = fact.fiscal_year
        self.fiscal_period = fact.fiscal_period
        self.form = fact.form
        self.filed = fact.filed
        self.facts_map = facts

    def get_facts_for_unit(self, fact_name, unit):
        """
        Get Fact for a given fact and unit
        @param fact_name: str, name of fact to retrieve
        @param unit: str, unit to retrieve
        @return: Fact
        """
        return self.facts_map[fact_name][unit]

    def list_all_facts(self):
        """
        Gets list of all available Facts w/in the given statement instance
        @return: List[Fact]
        """
        return self.facts_map.keys()

    def get_all_facts(self):
        """
        Returns all facts for the given Statement
        @return: dict, map of fact -> unit
        """
        return self.facts_map


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
        """
        Gets a Fact associated w/ a given unit
        @param key: str, unit to retrieve
        @return: Fact
        """
        return self.units.__dict__[key]

    def list_units(self):
        """
        List available units
        @return: List[str]
        """
        return list(self.units.__dict__.keys())

    def get_all_units(self):
        return self.units.__dict__.values()


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
