import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
INSTALL_REQUIRES = (HERE / "requirements.txt").read_text()

VERSION = "0.1.0-alpha"

setup(
    name="secpy",
    version=VERSION,
    author="Calvin Kessler",
    description=("Python library for interacting w/ the SEC REST API: https://www.sec.gov/edgar/sec-api-documentation"),
    license="MIT",
    install_requires=INSTALL_REQUIRES,
    keywords=["SEC", "EDGAR", "finance", "REST API wrapper"],
    url="https://github.com/McKalvan/secpy",
    download_url="https://github.com/user/reponame/archive/v{}.tar.gz".format(VERSION),
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
