import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from pyrdfstore import create_rdf_store
from rdflib import Graph

from pytravharv.common import QUERY_BUILDER
from pytravharv.store import TargetStoreAccess

load_dotenv()

TEST_INPUT_FOLDER = Path(__file__).parent / "./inputs"


@pytest.fixture()
def target_store():
    read_uri = os.getenv("TEST_SPARQL_READ_URI", None)
    write_uri = os.getenv("TEST_SPARQL_WRITE_URI", None)
    print(f"read_uri: {read_uri}")
    print(f"write_uri: {write_uri}")
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
