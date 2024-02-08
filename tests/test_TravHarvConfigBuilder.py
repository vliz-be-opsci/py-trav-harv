import os

import pytest

from pyTravHarv.TravHarvConfigBuilder import (
    AssertPath,
    AssertPathSet,
    LiteralSubjectDefinition,
    PrefixSet,
    SPARQLSubjectDefinition,
    SubjectDefinition,
    TravHarvConfigBuilder,
    TravHarvTask,
)

CFD = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILES_FOLDER = "/tests/config"


def test_build_from_config():
    builder = TravHarvConfigBuilder(CONFIG_FILES_FOLDER)
    # Test with a known config name
    builder.build_from_config("base_test.yml")
    assert builder.travHarvConfig is not None
    # Test with an unknown config name
    with pytest.raises(SystemExit):
        builder.build_from_config("unknown")


def test_build_from_folder():
    builder = TravHarvConfigBuilder(CONFIG_FILES_FOLDER)
    builder.build_from_folder()
    # Check that the config object was built
    assert builder.travHarvConfig is not None

    # Go over the builder.travHarvConfig and get the filenames by looping over the keys
    # and then check that the files exist in the config folder
    for filename in builder.travHarvConfig.keys():
        assert os.path.exists(os.path.join(CFD, CONFIG_FILES_FOLDER, filename))

    # Assure thatbad_config.yml is not in the builder.travHarvConfig
    assert "bad_config.yml" not in builder.travHarvConfig.keys()


def test_makeTravHarvConfigPartFromJson():
    builder = TravHarvConfigBuilder()
    json_object = {
        "prefix": {
            "prefix1": "http://example.com/",
            "prefix2": "http://example.org/",
        },
        "assert": [
            {
                "subjects": {
                    "literal": "subject1",
                },
                "paths": [
                    {
                        "Path_parts": ["path1", "path2"],
                        "max_size": lambda: 2,
                        "get_path_at_depth": lambda depth: f"path{depth}",
                    },
                    {
                        "Path_parts": ["path3", "path4"],
                        "max_size": lambda: 2,
                        "get_path_at_depth": lambda depth: f"path{depth}",
                    },
                ],
            },
            {
                "subjects": {
                    "SPARQL": "SELECT ?s WHERE { ?s ?p ?o }",
                },
                "paths": [
                    {
                        "Path_parts": ["path5", "path6"],
                        "max_size": lambda: 2,
                        "get_path_at_depth": lambda depth: f"path{depth}",
                    },
                ],
            },
        ],
    }

    result = builder._makeTravHarvConfigPartFromJson(json_object)

    assert isinstance(result["prefix_set"], PrefixSet)
    assert len(result["prefix_set"].prefixes) == 2

    assert isinstance(result["tasks"], list)
    assert len(result["tasks"]) == 2

    assert isinstance(result["tasks"][0], TravHarvTask)
    assert isinstance(result["tasks"][0].subject_definition, SubjectDefinition)
    assert isinstance(
        result["tasks"][0].subject_definition.definition, LiteralSubjectDefinition
    )
    assert isinstance(result["tasks"][0].assert_path_set, AssertPathSet)
    assert len(result["tasks"][0].assert_path_set.assert_paths) == 2

    assert isinstance(result["tasks"][1], TravHarvTask)
    assert isinstance(result["tasks"][1].subject_definition, SubjectDefinition)
    assert isinstance(
        result["tasks"][1].subject_definition.definition, SPARQLSubjectDefinition
    )
    assert isinstance(result["tasks"][1].assert_path_set, AssertPathSet)
    assert len(result["tasks"][1].assert_path_set.assert_paths) == 1


def test_check_subjects_literal_valid():
    builder = TravHarvConfigBuilder()
    subjects = {"literal": ["subject1", "subject2"]}
    assert builder._check_subjects(subjects) == True


def test_check_subjects_literal_invalid_type():
    builder = TravHarvConfigBuilder()
    subjects = {"literal": "subject1"}
    assert builder._check_subjects(subjects) == False


def test_check_subjects_literal_invalid_subjects():
    builder = TravHarvConfigBuilder()
    subjects = {"literal": ["subject1", 123]}
    assert builder._check_subjects(subjects) == False


def test_check_subjects_SPARQL_valid():
    builder = TravHarvConfigBuilder()
    subjects = {"SPARQL": "SELECT ?s WHERE { ?s ?p ?o }"}
    assert builder._check_subjects(subjects) == True


def test_check_subjects_SPARQL_invalid_type():
    builder = TravHarvConfigBuilder()
    subjects = {"SPARQL": ["SELECT ?s WHERE { ?s ?p ?o }"]}
    assert builder._check_subjects(subjects) == False


def test_check_subjects_SPARQL_invalid_query():
    builder = TravHarvConfigBuilder()
    subjects = {"SPARQL": "SELECT ?s WHERE { ?s ?p }"}
    assert builder._check_subjects(subjects) == False


def test_is_valid_sparql_syntax_valid():
    builder = TravHarvConfigBuilder()
    sparql_query = "SELECT ?s WHERE { ?s ?p ?o }"
    assert builder._is_valid_sparql_syntax(sparql_query) == True


def test_is_valid_sparql_syntax_invalid():
    builder = TravHarvConfigBuilder()
    sparql_query = "SELECT ?s WHERE { ?s ?p }"
    assert builder._is_valid_sparql_syntax(sparql_query) == False


def test_files_folder():
    builder = TravHarvConfigBuilder(CONFIG_FILES_FOLDER)
    result = builder._files_folder()
    assert isinstance(result, list)
    assert len(result) > 0
    for file in result:
        assert file.endswith(".yaml") or file.endswith(".yml")
        assert os.path.exists(file)


def test_load_yml_to_json_valid_file():
    builder = TravHarvConfigBuilder()
    file = "test_file.yml"
    json_object = builder._load_yml_to_json(file)
    assert isinstance(json_object, dict)


def test_load_yml_to_json_invalid_file():
    builder = TravHarvConfigBuilder()
    file = "nonexistent_file.yml"
    with pytest.raises(FileNotFoundError):
        builder._load_yml_to_json(file)


def test_load_yml_to_json_invalid_yaml():
    builder = TravHarvConfigBuilder()
    file = "invalid_yaml.yml"
    with pytest.raises(yaml.YAMLError):
        builder._load_yml_to_json(file)


def test_assert_dict_req_missing_fields():
    builder = TravHarvConfigBuilder()
    json_object = {
        "prefix": {
            "prefix1": "http://example.com/",
            "prefix2": "http://example.org/",
        },
        "assert": [
            {
                "subjects": {
                    "literal": "subject1",
                },
                "paths": [
                    {
                        "Path_parts": ["path1", "path2"],
                        "max_size": lambda: 2,
                        "get_path_at_depth": lambda depth: f"path{depth}",
                    },
                    {
                        "Path_parts": ["path3", "path4"],
                        "max_size": lambda: 2,
                        "get_path_at_depth": lambda depth: f"path{depth}",
                    },
                ],
            },
            {
                "subjects": {
                    "SPARQL": "SELECT ?s WHERE { ?s ?p ?o }",
                },
                "paths": [
                    {
                        "Path_parts": ["path5", "path6"],
                        "max_size": lambda: 2,
                        "get_path_at_depth": lambda depth: f"path{depth}",
                    },
                ],
            },
        ],
    }
    file = "test_file.yml"
    assert builder._assert_dict_req(json_object, file) == False


def test_assert_dict_req_missing_assert_fields():
    builder = TravHarvConfigBuilder()
    json_object = {
        "snooze-till-graph-age-minutes": 60,
        "prefix": {
            "prefix1": "http://example.com/",
            "prefix2": "http://example.org/",
        },
    }
    file = "test_file.yml"
    assert builder._assert_dict_req(json_object, file) == False


def test_assert_dict_req_valid():
    builder = TravHarvConfigBuilder()
    json_object = {
        "snooze-till-graph-age-minutes": 60,
        "prefix": {
            "prefix1": "http://example.com/",
            "prefix2": "http://example.org/",
        },
        "assert": [
            {
                "subjects": {
                    "literal": "subject1",
                },
                "paths": [
                    {
                        "Path_parts": ["path1", "path2"],
                        "max_size": lambda: 2,
                        "get_path_at_depth": lambda depth: f"path{depth}",
                    },
                    {
                        "Path_parts": ["path3", "path4"],
                        "max_size": lambda: 2,
                        "get_path_at_depth": lambda depth: f"path{depth}",
                    },
                ],
            },
            {
                "subjects": {
                    "SPARQL": "SELECT ?s WHERE { ?s ?p ?o }",
                },
                "paths": [
                    {
                        "Path_parts": ["path5", "path6"],
                        "max_size": lambda: 2,
                        "get_path_at_depth": lambda depth: f"path{depth}",
                    },
                ],
            },
        ],
    }
    file = "test_file.yml"
    assert builder._assert_dict_req(json_object, file) == True
