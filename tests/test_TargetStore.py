from pytravharv.rdfstoreaccess import TargetStore, _insert_resource_into_graph
from pytravharv.WebAccess import web_access
import os
import pytest
import re
import sys
import time
from typing import Optional, List
from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import (  # backup for validators since this cannot handle localhost
    quote,
    unquote,
    urlparse,
)
import rdflib
import requests
from pyrdfj2 import J2RDFSyntaxBuilder
from rdflib.plugins.sparql.processor import SPARQLResult
from SPARQLWrapper import JSON, SPARQLWrapper
from datetime import datetime
import validators


def test_select_subjects_memory_store():
    # Create an instance of TargetStore
    target_store = TargetStore(
        mode="memory",
        context=None,
    )

    # Define a sample SPARQL query
    sparql_query = "SELECT ?subject WHERE { ?subject rdf:type foaf:Person }"

    # Call the select_subjects method with the sample query
    result = target_store().select_subjects(sparql_query)

    # Assert that the result is of type SPARQLResult
    assert isinstance(result, SPARQLResult)

    # Assert that the result contains the expected bindings
    assert len(result.bindings) == 0


"""
def test_select_subjects_uri_store():
    # Create an instance of TargetStore
    # This test wil fail because I don't have a local graph store running
    target_store = TargetStore(
        mode="uristore",
        context=None,
        store_info=[
            "http://localhost:3030/ds/query",  # TODO: change to a valid graph store
            "http://localhost:3030/ds/update",
        ],
    )

    # Define a sample SPARQL query
    sparql_query = "SELECT ?subject WHERE { ?subject rdf:type foaf:Person }"

    # Call the select_subjects method with the sample query
    result = target_store().select_subjects(sparql_query)

    # Assert that the result is of type SPARQLResult
    assert isinstance(result, SPARQLResult)

    # Assert that the result contains the expected bindings
    assert len(result.bindings) == 0
"""


def test_verify_returns_true_memory_store():
    # Create an instance of TargetStore
    target_store = TargetStore(
        mode="memory",
        context=["./tests/inputs/63523.ttl"],
    )

    # Define a sample SPARQL query
    sparql_query = "SELECT ?subject WHERE { ?subject a <http://marineregions.org/ns/ontology#MRGeoObject> }"

    # Call the verify method with the sample query
    result = target_store().verify(sparql_query)

    # Assert that the result is True
    assert result is True


def test_verify_returns_false_memory_store():
    # Create an instance of TargetStore
    target_store = TargetStore(
        mode="memory",
        context=None,
    )

    # Define a sample SPARQL query
    sparql_query = "SELECT ?subject WHERE { ?subject a <http://marineregions.org/ns/ontology#MRGeoObject> }"

    # Call the verify method with the sample query
    result = target_store().verify(sparql_query)

    # Assert that the result is False
    assert result is False


def test_ingest_memory_store():
    # Create an instance of TargetStore
    target_store = TargetStore(
        mode="memory",
        context=None,
    )

    # Create a sample RDF graph
    graph = rdflib.Graph()
    graph.add(
        (
            rdflib.URIRef("http://example.org/subject1"),
            rdflib.URIRef("http://example.org/predicate"),
            rdflib.URIRef("http://example.org/object1"),
        )
    )
    graph.add(
        (
            rdflib.URIRef("http://example.org/subject2"),
            rdflib.URIRef("http://example.org/predicate"),
            rdflib.URIRef("http://example.org/object2"),
        )
    )

    # Call the ingest method with the sample graph
    target_store().ingest(graph)

    # Assert that the graph is ingested into the memory store
    assert len(target_store().graph) == 2


"""
def test_ingest_uri_store():
    # Create an instance of TargetStore
    # This test will fail because I don't have a local graph store running
    target_store = TargetStore(
        mode="uristore",
        context=None,
        store_info=[
            "http://localhost:3030/ds/query",  # TODO: change to a valid graph store
            "http://localhost:3030/ds/update",
        ],
    )

    # Create a sample RDF graph
    graph = rdflib.Graph()
    graph.add(
        (
            rdflib.URIRef("http://example.org/subject1"),
            rdflib.URIRef("http://example.org/predicate"),
            rdflib.URIRef("http://example.org/object1"),
        )
    )
    graph.add(
        (
            rdflib.URIRef("http://example.org/subject2"),
            rdflib.URIRef("http://example.org/predicate"),
            rdflib.URIRef("http://example.org/object2"),
        )
    )

    # Call the ingest method with the sample graph
    target_store().ingest(graph)

    # Assert that the graph is ingested into the URI store
    assert len(target_store().graph) == 2
"""


def test_insert_resource_into_graph_with_uri():
    # Create an empty graph
    graph = rdflib.Graph()

    # Define a sample URI
    uri = "https://marineregions.org/mrgid/3293.ttl"

    # Call the _insert_resource_into_graph function with the sample URI
    result = _insert_resource_into_graph(graph, uri)

    # Assert that the graph is not empty
    assert len(result) > 0


def test_insert_resource_into_graph_with_file_jsonld():
    # Create an empty graph
    graph = rdflib.Graph()

    # Define a sample JSON-LD file path
    file_path = "./tests/inputs/3293.jsonld"

    # Call the _insert_resource_into_graph function with the sample file path
    result = _insert_resource_into_graph(graph, file_path)

    # Assert that the graph is not empty
    assert len(result) > 0


def test_insert_resource_into_graph_with_file_ttl():
    # Create an empty graph
    graph = rdflib.Graph()

    # Define a sample Turtle file path
    file_path = "./tests/inputs/63523.ttl"

    # Call the _insert_resource_into_graph function with the sample file path
    result = _insert_resource_into_graph(graph, file_path)

    # Assert that the graph is not empty
    assert len(result) > 0


def test_insert_resource_into_graph_with_invalid_resource():
    # Create an empty graph
    graph = rdflib.Graph()

    # Define an invalid resource
    resource = "invalid_resource"

    # Call the _insert_resource_into_graph function with the invalid resource
    try:
        _insert_resource_into_graph(graph, resource)
    except ValueError:
        # Expected ValueError to be raised
        assert True
    else:
        # If ValueError is not raised, fail the test
        assert False
