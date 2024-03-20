import pytest
import os
from pathlib import Path
from pytravharv.store import URITargetStore, MemoryTargetStore
from pytravharv.common import QUERY_BUILDER
from rdflib import Graph
from dotenv import load_dotenv

load_dotenv()

TEST_INPUT_FOLDER = Path(__file__).parent / "./inputs"


@pytest.fixture()
def target_store():
    read_uri = os.getenv("TEST_SPARQL_READ_URI")
    write_uri = os.getenv("TEST_SPARQL_WRITE_URI")
    if read_uri is not None:
        return URITargetStore(QUERY_BUILDER, read_uri, write_uri)
    # else
    return MemoryTargetStore()


@pytest.fixture()
def prepopulated_target_store(target_store):
    graph = Graph()
    graph.parse(str(TEST_INPUT_FOLDER / "3293.jsonld"), format="json-ld")
    target_store.insert(graph)
    return target_store
