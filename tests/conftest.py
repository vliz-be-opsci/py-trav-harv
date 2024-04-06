import os
import shutil
from pathlib import Path

import pytest
from pyrdfstore import create_rdf_store
from rdflib import Graph
from util4tests import enable_test_logging

from travharv.common import QUERY_BUILDER
from travharv.store import TargetStoreAccess

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


@pytest.fixture()
def target_store():
    read_uri = os.getenv("TEST_SPARQL_READ_URI", None)
    write_uri = os.getenv("TEST_SPARQL_WRITE_URI", None)
    return create_rdf_store(None, None)
    return create_rdf_store(read_uri, write_uri)


@pytest.fixture()
def prepopulated_target_store(target_store):
    graph = Graph()
    graph.parse("tests/inputs/3293.jsonld", format="json-ld")
    target_store.insert(graph)
    return target_store


@pytest.fixture()
def target_store_access(target_store):
    return TargetStoreAccess(target_store, QUERY_BUILDER)
