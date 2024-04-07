import os
import shutil
from pathlib import Path

import pytest
from pyrdfstore import create_rdf_store
from rdflib import Graph
from util4tests import enable_test_logging

from travharv.store import RDFStoreAccess


TEST_FOLDER = Path(__file__).parent
TEST_CONFIG_FOLDER = TEST_FOLDER / "config"
TEST_INPUT_FOLDER = TEST_FOLDER / "inputs"
TEST_OUTPUT_FOLDER = TEST_FOLDER / "output"


# enables logging for all test
# also includes load_dotenv for all
enable_test_logging()


@pytest.fixture()
def outpath() -> Path:
    # note we clean the folder at the start
    # and keeping it at the end -- so the folder can be expected after test
    shutil.rmtree(str(TEST_OUTPUT_FOLDER), ignore_errors=True)  # always clean
    TEST_OUTPUT_FOLDER.mkdir(exist_ok=True, parents=True)  # and recreate
    return TEST_OUTPUT_FOLDER


@pytest.fixture(scope="session")
def _mem_store_info():
    return ()


@pytest.fixture(scope="session")
def _uri_store_info():
    read_uri: str = os.getenv("TEST_SPARQL_READ_URI", None)
    write_uri: str = os.getenv("TEST_SPARQL_WRITE_URI", read_uri)
    if read_uri is None or write_uri is None:
        return None
    # else
    return (read_uri, write_uri)


@pytest.fixture(scope="session")
def store_info_sets(_mem_store_info, _uri_store_info):
    return tuple(
        storeinfo
        for storeinfo in (_mem_store_info, _uri_store_info)
        if storeinfo is not None
    )


@pytest.fixture(scope="session")
def rdf_stores(store_info_sets):
    return (create_rdf_store(*storeinfo) for storeinfo in store_info_sets)


@pytest.fixture(scope="session")
def decorated_rdf_stores(rdf_stores):
    return (RDFStoreAccess(rdf_store) for rdf_store in rdf_stores)


def loadfilegraph(fname, format="json-ld"):
    graph = Graph()
    graph.parse(fname, format=format)
    return graph


@pytest.fixture()
def sample_file_graph():
    """graph loaded from specific input file
    in casu: tests/input/3293.jsonld
    """
    return loadfilegraph(str(TEST_INPUT_FOLDER / "3293.jsonld"))
