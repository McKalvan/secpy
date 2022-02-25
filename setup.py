import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

PACKAGE_NAME = "sec-python"
VERSION = "0.4.0-alpha"

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author="Calvin Kessler",
    description=("Python library for interacting w/ the SEC REST API: https://www.sec.gov/edgar/sec-api-documentation"),
    license="MIT",
    install_requires=["requests==2.27.1",
                      "backoff==1.11.1",
                      "ratelimiter==1.2.0",
                      "tqdm==4.62.3"
                      ],
    keywords=["SEC", "EDGAR", "finance", "REST API wrapper"],
    url="https://github.com/McKalvan/secpy",
    download_url="https://github.com/McKalvan/secpy/archive/refs/tags/v{}.zip".format(VERSION),
    packages=find_packages(exclude="tests"),
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"
    ]
)
