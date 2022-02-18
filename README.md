# secpy
secpy is Python package for accessing data on the [SEC's REST API](https://www.sec.gov/edgar/sec-api-documentation). 
The primary objective of secpy is to provide an intuitive way of programmatically processing SEC data while keeping respecting
the [SEC's acceptable use policy](https://www.sec.gov/privacy.htm#security) behind the scenes. Simply supply a User-Agent 
to identify your application and secpy will handle the internal rate-limiting, so there is no need to worry about being
temporarily banned or blacklisted by the SEC's REST API.

### Installation
secpy is supported on Python 3+. secpy can be installed via [pip](https://pypi.org/project/pip/) as follows:

`pip install sec-python`

Verify the installation by running the following:

`pip show sec-python`

### Quick Start
The easiest way to get started with secpy is to instantiate a SECPyClient instance w/ a User-Agent to identify
your application:

```python
from secpy.secpy_client import SECPyClient
client = SECPyClient("<YOUR USER-AGENT>")
```
Data from any endpoint can then be accessed as a method of the client as follows:
```python
from secpy.secpy_client import SECPyClient
client = SECPyClient("<YOUR USER-AGENT>")

# CompanyFactsEndpoint
client.company_facts()

# SubmissionsEndpoint
client.submissions()

#CompanyConceptEndpoint
client.company_concepts()

# FramesEndpoint
client.frames()
```

Each of the above endpoint methods in the client creates an endpoint object that provides one or more ways w/ which data 
from that endpoint can be retrieved and parsed into respective data objects.  For example, the following retrieves company facts for Microsoft and 
then retrieves the most recent value for "Assets" reported by the Microsoft to the SEC:

```python
from secpy.secpy_client import SECPyClient
client = SECPyClient("<YOUR USER-AGENT>")
company_facts = client.company_facts()
msft = company_facts.get_company_facts_for_ticker("MSFT")

# Gets the most recent value of Assets (reported in USD) for MSFT 
msft.get_concept(taxonomy="us_gaap", concept="Assets").get_unit("USD")[0].value
# Alternatively, this is statement to the previous
msft.taxonomies.us_gaap.Assets.units.USD[0].value
```

CIKs (Central Index Key) are commonly used throughout the SEC API to access information on a specific company, so there
is also an additional method w/in the SECPyClient that creates an instance of TickerCompanyExchangeMap. This allows for
conversion between the ticker that a particular commonly uses on exchanges to the CIK value that the SEC uses to represent
that company internally. This class also allows for additional insight into the name and exchange (if any) that the company
can be found on. 

```python
from secpy.secpy_client import SECPyClient
client = SECPyClient("<YOUR USER-AGENT>")
ticker_company_exchange_map = client.ticker_company_exchange_map()
ticker_company_exchange_map.lookup_ticker("MSFT")
```

Note: Companies w/out tickers (typically unlisted companies) will NOT appear in TickerCompanyExchangeMap.

In addition to all endpoints documented [here](https://www.sec.gov/edgar/sec-api-documentation), secpy also supports 
ingesting the bulk submissions and company facts zip files.

```python
from secpy.secpy_client import SECPyClient
client = SECPyClient("<YOUR USER-AGENT>")

# Instantiate and call download_bulk_data() or any other public method to download bulk submissions zip file
bulk_submissions = client.bulk_submissions()
bulk_submissions.download_bulk_data()
bulk_submissions.get_data_for_ticker_from_archive("MSFT")

# Or use existing bulk submissions zip file
bulk_submissions = client.bulk_submissions(existing_archive="<PATH TO ARCHIVE>")
bulk_submissions.get_data_for_ticker_from_archive("MSFT")

# Same general principles apply to bulk company facts
bulk_company_facts = client.bulk_company_facts()
bulk_company_facts.download_bulk_data()
bulk_company_facts.get_data_for_ticker_from_archive("MSFT")
```
NOTE: The bulk submission zip file generally will take some time to process after it is downloaded due to the number of files 
that are currently in that zip file. 

Bulk data files are downloaded into the temp directory and can be persisted by invoking `persist_zipfile` on the bulk data object.
Bulk data objects that are not persisted and go out of scope will automatically be cleaned.

### Versioning
Releases of secpy are planned to follow a semantic versioning strategy as specified in [this link](https://semver.org/).

### Contributing to secpy
Any/all contributions are welcomed and encouraged especially in the early stages of development for secpy! If you have an idea for how secpy can be 
improved or if you have identified and fixed any bugs w/ secpy, please feel free to raise a PR against the latest release version. 
Other ways to contribute to secpy include, but are certainly not limited to, creating bugfix tickets for existing issues, 
writing better documentation, and improving on unit test coverage in secpy.

### Future areas of exploration
The following are areas worthy of potential exploration in secpy:
- Adding support for SEC EDGAR Full Text search: https://www.sec.gov/edgar/search/

### Licensing
All versions of secpy are currently provided under the [MIT License](https://mit-license.org/)
