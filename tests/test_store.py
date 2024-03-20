#! /usr/bin/env python
from util4tests import run_single_test
import pytest
from string import ascii_lowercase
from pytravharv.store import TargetStoreAccess, TargetStore, URITargetStore
import datetime
import math
import random
from rdflib import Graph, URIRef, BNode, Literal
import datetime
from pytravharv.common import QUERY_BUILDER


@pytest.mark.usefixtures("prepopulated_target_store")
def test_select_subjects(prepopulated_target_store):
    assert (
        prepopulated_target_store is not None
    ), "can't perform test without target store"
    sparql = "SELECT ?subject ?p WHERE { ?subject ?p ?o }"
    tsa = TargetStoreAccess(prepopulated_target_store, QUERY_BUILDER)
    subjects = tsa.select_subjects(sparql)
    assert isinstance(subjects, list)
    assert len(subjects) > 0
    # Add more assertions as needed


@pytest.mark.usefixtures("target_store")
def test_insert(target_store):
    graph = Graph()
    context = "test_context"

    len_insert_graph = len(graph)

    # get length graph before insert
    result = target_store.select("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
    len_before = len(result)

    # Insert graph without context
    target_store.insert(graph)

    assert len(graph) == len_insert_graph, "graph should not be modified"


@pytest.mark.usefixtures("target_store")
def test_big_insert_triple(target_store):
    graph = Graph()
    graph.parse(
        "tests/inputs/marineinfo-publication-288351.jsonld", format="json-ld"
    )
    target_store.insert(graph)

    all_triples = target_store.select("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")

    assert len(all_triples) > 0


@pytest.mark.usefixtures("target_store")
def test_lastmod_for_context(target_store):

    # Add test data to the TargetStore
    context = "urn:test_context"
    test_graph = Graph()
    target_store.insert(test_graph, context)

    # Test the lastmod_for_context method
    lastmod = target_store.lastmod_for_context(context)
    print(lastmod)
    assert isinstance(lastmod, datetime.datetime)
    assert lastmod < datetime.datetime.now()


@pytest.mark.usefixtures("target_store_access")
def test_verify(target_store_access):
    subject = "http://example.org/subject"
    property_path = "<http://example.org/property>"
    assert target_store_access.verify(subject, property_path) == False


@pytest.mark.usefixtures("target_store_access_memory")
def test_verify_memory(target_store_access_memory):
    subject = "http://example.org/subject"
    property_path = "<http://example.org/property>"
    assert target_store_access_memory.verify(subject, property_path) == False


@pytest.mark.usefixtures("prepopulated_target_store_access_memory")
def test_verify_memory(prepopulated_target_store_access_memory):

    tsa = prepopulated_target_store_access_memory

    subject = "http://marineregions.org/mrgid/2419"
    property_path = "<http://www.w3.org/2004/02/skos/core#prefLabel>"

    assert tsa.verify(subject, property_path) == True


if __name__ == "__main__":
    run_single_test(__file__)
