import pathlib

import pytest
from rdflib import Graph

from pytravharv.common import insert_resource_into_graph

INPUT_PATH = pathlib.Path(__file__).parent / "inputs"


@pytest.fixture
def test_graph():
    return Graph()


def test_insert_resource_into_graph_uri(test_graph):
    uri = "https://www.w3.org/People/Berners-Lee/card.ttl"
    graph = insert_resource_into_graph(test_graph, uri)
    assert isinstance(graph, Graph)
    assert len(graph) > 0


def test_insert_resource_into_graph_file_jsonld(test_graph):
    file_path = str(INPUT_PATH / "3293.jsonld")
    graph = insert_resource_into_graph(test_graph, file_path)
    assert isinstance(graph, Graph)
    assert len(graph) > 0


def test_insert_resource_into_graph_file_ttl(test_graph):
    file_path = str(INPUT_PATH / "63523.ttl")
    graph = insert_resource_into_graph(test_graph, file_path)
    assert isinstance(graph, Graph)
    assert len(graph) > 0


def test_insert_resource_into_graph_invalid_resource(test_graph):
    resource = "invalid_resource"
    with pytest.raises(ValueError):
        insert_resource_into_graph(test_graph, resource)
