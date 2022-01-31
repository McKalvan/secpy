from secpy.company_facts import CompanyFactsEndpoint, CompanyFactsBulkEndpoint
from secpy.submissions import SubmissionsEndpoint, SubmissionsBulkEndpoint
from secpy.company_concept import CompanyConceptEndpoint
from secpy.frames import FramesEndpoint
from secpy.core.ticker_company_exchange_map import TickerCompanyExchangeMap


class SECPyClient:
    def __init__(self, user_agent):
        self.user_agent = user_agent

    def submissions(self, **kwargs):
        return SubmissionsEndpoint(self.user_agent, **kwargs)

    def bulk_submissions(self, existing_archive=None,  **kwargs):
        return SubmissionsBulkEndpoint(self.user_agent, existing_archive, **kwargs)

    def company_facts(self, **kwargs):
        return CompanyFactsEndpoint(self.user_agent, **kwargs)

    def bulk_company_facts(self, existing_archive=None, **kwargs):
        return CompanyFactsBulkEndpoint(self.user_agent, existing_archive, **kwargs)

    def company_concepts(self, **kwargs):
        return CompanyConceptEndpoint(self.user_agent, **kwargs)

    def frames(self, **kwargs):
        return FramesEndpoint(self.user_agent, **kwargs)

    def ticker_company_exchange_map(self, **kwargs):
        return TickerCompanyExchangeMap(self.user_agent, **kwargs)
