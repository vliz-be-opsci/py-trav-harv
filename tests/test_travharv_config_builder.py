from util4tests import run_single_test
import pytest
from string import ascii_lowercase
from pytravharv.TravHarvConfigBuilder import (
    TravHarvConfigBuilder,
    SPARQLSubjectDefinition,
    LiteralSubjectDefinition,
    AssertPathSet,
    AssertPath,
)
import pathlib
import datetime
import math
import random
from rdflib import Graph, URIRef, BNode, Literal
import datetime
from pytravharv.common import QUERY_BUILDER

CONFIG_FOLDER = pathlib.Path(__file__).parent / "config"
INPUT_FOLDER = pathlib.Path(__file__).parent / "inputs"


@pytest.mark.usefixtures("target_store_access_memory")
def test_good_config_builder(target_store_access_memory):
    # first populate the memory store with some data
    graph = Graph()
    graph.parse(str(INPUT_FOLDER / "3293.jsonld"), format="json-ld")
    target_store_access_memory.ingest(graph, "uri:PYTRAVHARV:base_test.yml")

    # travharvconfigbuilder
    travharvconfigbuilder = TravHarvConfigBuilder(
        target_store_access_memory,
        str(CONFIG_FOLDER / "good_folder"),
    )

    travharvconfigbuilder.build_from_config("base_test.yml")

    assert travharvconfigbuilder is not None
    assert True


@pytest.mark.usefixtures("target_store_access_memory")
def test_bad_config_builder(target_store_access_memory):
    # first populate the memory store with some data
    graph = Graph()
    graph.parse(str(INPUT_FOLDER / "3293.jsonld"), format="json-ld")
    target_store_access_memory.ingest(graph, "uri:PYTRAVHARV:base_test.yml")

    # travharvconfigbuilder
    travharvconfigbuilder = TravHarvConfigBuilder(
        target_store_access_memory,
        str(CONFIG_FOLDER),
    )
    # the following command should raise an exception
    with pytest.raises(Exception):
        travharvconfigbuilder.build_from_config("bad_config.yml")


def test_literal_subject_definition():
    # literal subject definition
    subjects = [
        "http://www.w3.org/2000/01/rdf-schema#label",
        "http://www.w3.org/2000/01/rdf-schema#comment",
    ]

    literal_subject_definition = LiteralSubjectDefinition(subjects)
    assert literal_subject_definition is not None

    assert literal_subject_definition() == subjects
    assert literal_subject_definition.listSubjects() == subjects


@pytest.mark.usefixtures("target_store_access_memory")
def test_sparql_subject_definition(target_store_access_memory):
    graph = Graph()
    graph.parse(str(INPUT_FOLDER / "3293.jsonld"), format="json-ld")
    target_store_access_memory.ingest(graph, "uri:PYTRAVHARV:base_test.yml")

    # sparql subject definition
    sparql = "SELECT ?subject ?p WHERE { ?subject ?p ?o }"
    sparql_subject_definition = SPARQLSubjectDefinition(
        sparql, target_store_access_memory
    )

    assert sparql_subject_definition is not None
    assert len(sparql_subject_definition()) > 0
    assert len(sparql_subject_definition.listSubjects()) == 99


def test_assert_path():
    assertion_path_str = (
        "mr:isPartOf/<https://schema.org/geo>/<https://schema.org/latitude>"
    )
    assertion_path = AssertPath(assertion_path_str)

    assert assertion_path is not None
    assert str(assertion_path) == assertion_path_str
    assert assertion_path.get_max_size() == 3
    assert assertion_path.get_path_parts() == [
        "mr:isPartOf",
        "<https://schema.org/geo>",
        "<https://schema.org/latitude>",
    ]
    assert assertion_path.get_path_for_depth(1) == "mr:isPartOf"
    assert (
        assertion_path.get_path_for_depth(2)
        == "mr:isPartOf/<https://schema.org/geo>"
    )


if __name__ == "__main__":
    run_single_test(__file__)
