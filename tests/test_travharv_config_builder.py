import pathlib

import pytest
from rdflib import Graph
from util4tests import run_single_test

from pytravharv.TravHarvConfigBuilder import (
    AssertPath,
    LiteralSubjectDefinition,
    SPARQLSubjectDefinition,
    TravHarvConfigBuilder,
)
from pytravharv.TravHarvExecuter import TravHarvExecutor

CONFIG_FOLDER = pathlib.Path(__file__).parent / "config"
INPUT_FOLDER = pathlib.Path(__file__).parent / "inputs"
OUTPUT_FOLDER = pathlib.Path(__file__).parent / "output"

if not OUTPUT_FOLDER.exists():
    OUTPUT_FOLDER.mkdir()

# clean up the output folder
for file in OUTPUT_FOLDER.glob("*"):
    file.unlink()


@pytest.mark.usefixtures("target_store_access")
def test_good_config_builder(target_store_access):
    # first populate the memory store with some data
    graph = Graph()
    graph.parse(str(INPUT_FOLDER / "3293.jsonld"), format="json-ld")
    target_store_access.ingest(graph, "uri:PYTRAVHARV:base_test.yml")

    # travharvconfigbuilder
    travharvconfigbuilder = TravHarvConfigBuilder(
        target_store_access,
        str(CONFIG_FOLDER / "good_folder"),
    )

    travharvconfigbuilder.build_from_config("base_test.yml")

    assert travharvconfigbuilder is not None
    assert True


@pytest.mark.usefixtures("target_store_access")
def test_bad_config_builder(target_store_access):
    # first populate the memory store with some data
    graph = Graph()
    graph.parse(str(INPUT_FOLDER / "3293.jsonld"), format="json-ld")
    target_store_access.ingest(graph, "uri:PYTRAVHARV:base_test.yml")

    # travharvconfigbuilder
    travharvconfigbuilder = TravHarvConfigBuilder(
        target_store_access,
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


@pytest.mark.usefixtures("target_store_access")
def test_sparql_subject_definition(target_store_access):
    graph = Graph()
    graph.parse(str(INPUT_FOLDER / "3293.jsonld"), format="json-ld")
    target_store_access.ingest(graph, "uri:PYTRAVHARV:base_test.yml")

    # sparql subject definition
    sparql = "SELECT ?subject ?p WHERE { ?subject ?p ?o }"
    sparql_subject_definition = SPARQLSubjectDefinition(
        sparql, target_store_access
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


@pytest.mark.usefixtures("target_store_access")
def test_travharvconfig(target_store_access):
    graph = Graph()
    graph.parse(str(INPUT_FOLDER / "3293.jsonld"), format="json-ld")
    target_store_access.ingest(graph, "uri:PYTRAVHARV:base_test.yml")

    # travharvconfig
    travharvconfig = TravHarvConfigBuilder(
        target_store_access,
        str(CONFIG_FOLDER / "good_folder"),
    ).build_from_config("base_test.yml")

    assert travharvconfig is not None
    print(travharvconfig)

    # config should contain the following keys
    assert "configname" in travharvconfig()
    assert "prefixset" in travharvconfig()
    assert "tasks" in travharvconfig()

    assert travharvconfig.configname == "base_test.yml"
    assert len(travharvconfig.prefixset) == 3
    assert len(travharvconfig.tasks) == 3


@pytest.mark.usefixtures("target_store_access")
def test_travharv_config_builder_from_folder(target_store_access):
    travharvconfigbuilder = TravHarvConfigBuilder(
        target_store_access,
        str(CONFIG_FOLDER / "good_folder"),
    )

    travharvconfiglist = travharvconfigbuilder.build_from_folder()

    assert len(travharvconfiglist) == 2


@pytest.mark.usefixtures("target_store_access")
def test_travharv_config_builder_from_folder_bad(target_store_access):
    travharvconfigbuilder = TravHarvConfigBuilder(
        target_store_access,
        str(CONFIG_FOLDER / "bad_folder"),
    )

    with pytest.raises(Exception):
        travharvconfigbuilder.build_from_folder()


@pytest.mark.usefixtures("target_store_access")
def test_check_snooze(target_store_access):
    graph = Graph()
    graph.parse(str(INPUT_FOLDER / "3293.jsonld"), format="json-ld")
    target_store_access.ingest(graph, "uri:PYTRAVHARV:base_test.yml")

    travharvconfigbuilder = TravHarvConfigBuilder(
        target_store_access,
        str(CONFIG_FOLDER / "good_folder"),
    )

    test_pass = travharvconfigbuilder._check_snooze(10, "base_test.yml")
    assert test_pass is False


@pytest.mark.usefixtures("target_store_access")
def test_run_good_config(target_store_access):
    graph = Graph()
    graph.parse(str(INPUT_FOLDER / "63523.ttl"), format="turtle")
    target_store_access.ingest(graph, "uri:PYTRAVHARV:base_test.yml")

    travharvconfigbuilder = TravHarvConfigBuilder(
        target_store_access,
        str(CONFIG_FOLDER / "good_folder"),
    )

    travharvconfig = travharvconfigbuilder.build_from_config("base_test.yml")

    travharvexecutor = TravHarvExecutor(
        travharvconfig.configname,
        travharvconfig.prefixset,
        travharvconfig.tasks,
        target_store_access,
        str(OUTPUT_FOLDER / "output.ttl"),
    )

    travharvexecutor.assert_all_paths()


if __name__ == "__main__":
    run_single_test(__file__)
