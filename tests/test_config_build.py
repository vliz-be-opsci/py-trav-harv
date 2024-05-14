#!/usr/bin/env python
import pytest
from conftest import TEST_CONFIG_FOLDER
from util4tests import run_single_test

from travharv.config_build import (
    AssertPath,
    LiteralSubjectDefinition,
    SPARQLSubjectDefinition,
    TravHarvConfigBuilder,
)
from travharv.helper import makeNSM, resolve_ppaths


@pytest.mark.usefixtures("decorated_rdf_stores", "sample_file_graph")
def test_good_config_builder(decorated_rdf_stores, sample_file_graph):
    for rdf_store in decorated_rdf_stores:
        # first populate the memory store with some data
        rdf_store.insert(sample_file_graph, "urn:test:good-config:base")

        # travharvconfigbuilder
        travharvconfigbuilder = TravHarvConfigBuilder(
            rdf_store,
            str(TEST_CONFIG_FOLDER / "good_folder"),
        )

        assert travharvconfigbuilder is not None
        cfg = travharvconfigbuilder.build_from_config("base_test.yml")

        assert cfg is not None

        # TODO assert more details from base_test.yml


@pytest.mark.usefixtures("decorated_rdf_stores", "sample_file_graph")
def test_bad_config_builder(decorated_rdf_stores, sample_file_graph):
    for rdf_store in decorated_rdf_stores:
        # first populate the memory store with some data
        rdf_store.insert(sample_file_graph, "urn:test:bad-config:base")

        # travharvconfigbuilder
        travharvconfigbuilder = TravHarvConfigBuilder(
            rdf_store,
            str(TEST_CONFIG_FOLDER),
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

    assert literal_subject_definition.list_subjects() == subjects


@pytest.mark.usefixtures("decorated_rdf_stores", "sample_file_graph")
def test_sparql_subject_definition(decorated_rdf_stores, sample_file_graph):
    sparql = "SELECT ?subject ?p WHERE { ?subject ?p ?o }"

    for rdf_store in decorated_rdf_stores:
        # first populate the memory store with some data
        rdf_store.insert(sample_file_graph, "urn:test:subject-definition:base")

        # sparql subject definition
        sparql_subject_definition = SPARQLSubjectDefinition(sparql, rdf_store)

        assert sparql_subject_definition is not None
        assert len(sparql_subject_definition()) > 0
        assert len(sparql_subject_definition.listSubjects()) == 99


yml_pfx_declarations = dict(
    schema="https://schema.org#",
    ex="https://example.org/",
)


def test_assert_path():
    NSM = makeNSM(yml_pfx_declarations)

    resolved_ppaths = resolve_ppaths(
        [
            "schema:geo/ex:example/<https://marineregions.org#test>",
        ],
        NSM,
    )

    assertion_path = AssertPath(resolved_ppaths[0])

    assert assertion_path is not None
    assert assertion_path.get_max_size() == 3
    assert assertion_path.get_path_parts() == [
        "<https://schema.org#geo>",
        "<https://example.org/example>",
        "<https://marineregions.org#test>",
    ]
    assert assertion_path.get_path_for_depth(1) == "<https://schema.org#geo>"
    assert (
        assertion_path.get_path_for_depth(2)
        == "<https://schema.org#geo>/<https://example.org/example>"
    )


@pytest.mark.usefixtures("decorated_rdf_stores", "sample_file_graph")
def test_travharvconfig(decorated_rdf_stores, sample_file_graph):
    for rdf_store in decorated_rdf_stores:
        # first populate the memory store with some data
        rdf_store.insert(sample_file_graph, "urn:test:travharv-config:base")

        # travharvconfig
        travharvconfig = TravHarvConfigBuilder(
            rdf_store,
            str(TEST_CONFIG_FOLDER / "good_folder"),
        ).build_from_config("base_test.yml")

        assert travharvconfig is not None

        # config should contain the following keys
        assert "configname" in travharvconfig()
        assert "NPM" in travharvconfig()
        assert "tasks" in travharvconfig()

        assert travharvconfig.configname == "base_test.yml"
        assert len(travharvconfig.tasks) == 3


@pytest.mark.usefixtures("decorated_rdf_stores", "sample_file_graph")
def test_travharv_config_builder_from_folder(
    decorated_rdf_stores, sample_file_graph
):
    for rdf_store in decorated_rdf_stores:
        # first populate the memory store with some data
        rdf_store.insert(
            sample_file_graph, "urn:test:travharv-config-build-folder:base"
        )

        travharvconfigbuilder = TravHarvConfigBuilder(
            rdf_store,
            str(TEST_CONFIG_FOLDER / "good_folder"),
        )

        travharvconfiglist = travharvconfigbuilder.build_from_folder()

        assert len(travharvconfiglist) == 2


@pytest.mark.usefixtures("decorated_rdf_stores", "sample_file_graph")
def test_travharv_config_builder_from_folder_bad(
    decorated_rdf_stores, sample_file_graph
):
    for rdf_store in decorated_rdf_stores:
        # first populate the memory store with some data
        rdf_store.insert(
            sample_file_graph, "urn:test:travharv-config-build-folder-bad:base"
        )

        travharvconfigbuilder = TravHarvConfigBuilder(
            rdf_store,
            str(TEST_CONFIG_FOLDER / "bad_folder"),
        )

        with pytest.raises(Exception):
            travharvconfigbuilder.build_from_folder()


if __name__ == "__main__":
    run_single_test(__file__)
