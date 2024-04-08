#!/usr/bin/env python
import pytest
from conftest import TEST_INPUT_FOLDER
from rdflib import Graph
from util4tests import run_single_test

from travharv.__main__ import load_resource_into_graph


def test_insert_resource_into_graph_uri():
    uri = "https://www.w3.org/People/Berners-Lee/card.ttl"
    graph = load_resource_into_graph(Graph(), uri)
    assert isinstance(graph, Graph)
    assert len(graph) > 0


def test_insert_resource_into_graph_file_jsonld():
    file_path = str(TEST_INPUT_FOLDER / "3293.jsonld")
    graph = load_resource_into_graph(Graph(), file_path)
    assert isinstance(graph, Graph)
    assert len(graph) > 0


def test_insert_resource_into_graph_file_ttl():
    file_path = str(TEST_INPUT_FOLDER / "63523.ttl")
    graph = load_resource_into_graph(Graph(), file_path)
    assert isinstance(graph, Graph)
    assert len(graph) > 0


def test_insert_resource_into_graph_invalid_resource():
    resource = "invalid_resource"
    with pytest.raises(ValueError):
        load_resource_into_graph(Graph(), resource)


if __name__ == "__main__":
    run_single_test(__file__)
