from py import test
from pytravharv import TravHarvConfigBuilder, TargetStore
from pytravharv.TravHarvConfigBuilder import (
    TravHarvConfig,
    AssertPathSet,
    LiteralSubjectDefinition,
    AssertPath,
)
import os
import pytest
from datetime import datetime, timedelta

mode = "memory"
config_folder = "./tests/config"
bad_config_folder = "./tests/config"
good_config_folder = "./tests/config/good_folder"
name_good_config = "base_test.yml"
name_bad_config = "bad_config.yml"


def test_build_from_config():
    # Create a test instance of TravHarvConfigBuilder
    config_folder = "./tests/config"
    test_target_store = TargetStore(
        mode="memory",
        context=["./tests/inputs/63523.ttl"],
    )
    builder = TravHarvConfigBuilder(
        test_target_store,
        config_folder,
    )

    # Define test inputs
    config_name = "base_test.yml"

    # Call the method under test
    result = builder.build_from_config(config_name)

    # Perform assertions on the result
    assert isinstance(result, TravHarvConfig)
    # Add more assertions as needed


def test_build_from_folder():
    # Create a test instance of TravHarvConfigBuilder
    test_target_store = TargetStore(
        mode="memory",
        context=["./tests/inputs/63523.ttl"],
    )
    builder = TravHarvConfigBuilder(
        test_target_store,
        good_config_folder,
    )

    # Call the method under test
    result = builder.build_from_folder()

    # Perform assertions on the result
    assert isinstance(result, list)
    assert all(isinstance(config, TravHarvConfig) for config in result)
    assert len(result) == 2  # Assuming there are 2 config files in the folder

    # Add more assertions as needed


def test_build_from_folder_failure_assertion():
    # Create a test instance of TravHarvConfigBuilder
    test_target_store = TargetStore(
        mode="memory",
        context=["./tests/inputs/63523.ttl"],
    )
    builder = TravHarvConfigBuilder(
        test_target_store,
        bad_config_folder,
    )

    # Call the method under test
    with pytest.raises(Exception):
        result = builder.build_from_folder()


def test__assert_subjects():
    # Create a test instance of TravHarvConfigBuilder
    test_target_store = TargetStore(
        mode="memory",
        context=["./tests/inputs/63523.ttl"],
    )
    builder = TravHarvConfigBuilder(
        test_target_store,
        config_folder,
    )

    # Define test inputs
    subjects = {
        "literal": ["subject1", "subject2"],
        "SPARQL": "SELECT ?s WHERE { ?s ?p ?o }",
    }

    # Call the method under test
    builder._assert_subjects(subjects)

    # No assertions needed as the method should raise an exception if any assertion fails


def test__assert_subjects_invalid_subjects():
    # Create a test instance of TravHarvConfigBuilder
    test_target_store = TargetStore(
        mode="memory",
        context=["./tests/inputs/63523.ttl"],
    )
    builder = TravHarvConfigBuilder(
        test_target_store,
        config_folder,
    )

    # Define test inputs
    subjects = {
        "invalid_key": "value",
    }

    # Call the method under test
    with pytest.raises(Exception):
        builder._assert_subjects(subjects)


def test__assert_subjects_invalid_literal_subjects():
    # Create a test instance of TravHarvConfigBuilder
    test_target_store = TargetStore(
        mode="memory",
        context=["./tests/inputs/63523.ttl"],
    )
    builder = TravHarvConfigBuilder(
        test_target_store,
        config_folder,
    )

    # Define test inputs
    subjects = {
        "literal": "invalid_subject",
    }

    # Call the method under test
    with pytest.raises(Exception):
        builder._assert_subjects(subjects)


def test__assert_subjects_invalid_sparql_subjects():
    # Create a test instance of TravHarvConfigBuilder
    test_target_store = TargetStore(
        mode="memory",
        context=["./tests/inputs/63523.ttl"],
    )
    builder = TravHarvConfigBuilder(
        test_target_store,
        config_folder,
    )

    # Define test inputs
    subjects = {
        "SPARQL": ["invalid_subject"],
    }

    # Call the method under test
    with pytest.raises(Exception):
        builder._assert_subjects(subjects)


def test__assert_subjects_invalid_sparql_syntax():
    # Create a test instance of TravHarvConfigBuilder
    test_target_store = TargetStore(
        mode="memory",
        context=["./tests/inputs/63523.ttl"],
    )
    builder = TravHarvConfigBuilder(
        test_target_store,
        config_folder,
    )

    # Define test inputs
    subjects = {
        "SPARQL": "SELECT ?s WHERE { ?s ?p ?o",
    }

    # Call the method under test
    with pytest.raises(Exception):
        builder._assert_subjects(subjects)


def test__makeTravHarvConfigPartFromDict():
    # Create a test instance of TravHarvConfigBuilder
    test_target_store = TargetStore(
        mode="memory",
        context=["./tests/inputs/63523.ttl"],
    )
    builder = TravHarvConfigBuilder(
        test_target_store,
        config_folder,
    )

    # Define test inputs
    dict_object = {
        "snooze-till-graph-age-minutes": 60,
        "assert": [
            {
                "subjects": {
                    "literal": ["subject1", "subject2"],
                    "SPARQL": "SELECT ?s WHERE { ?s ?p ?o }",
                },
                "paths": ["path1", "path2"],
            }
        ],
        "prefix": "prefix",
    }
    name_config = "default"

    # Call the method under test
    result = builder._makeTravHarvConfigPartFromDict(dict_object, name_config)
    # Perform assertions on the result
    assert isinstance(result, TravHarvConfig)
    assert result.configname == name_config
    assert result.prefixset == dict_object["prefix"]
    assert len(result.tasks) == 1
    assert isinstance(
        result.tasks[0].subject_definition, LiteralSubjectDefinition
    )
    assert isinstance(result.tasks[0].assert_path_set, AssertPathSet)
    assert len(result.tasks[0].assert_path_set()) == 2
    # Add more assertions as needed


def test__makeTravHarvConfigPartFromDict_missing_snooze_minutes():
    # Create a test instance of TravHarvConfigBuilder
    test_target_store = TargetStore(
        mode="memory",
        context=["./tests/inputs/63523.ttl"],
    )
    builder = TravHarvConfigBuilder(
        test_target_store,
        config_folder,
    )

    # Define test inputs
    dict_object = {
        "assert": [
            {
                "subjects": {
                    "literal": ["subject1", "subject2"],
                    "SPARQL": "SELECT ?s WHERE { ?s ?p ?o }",
                },
                "paths": ["path1", "path2"],
            }
        ],
        "prefix": "prefix",
    }
    name_config = "default"

    # Call the method under test
    with pytest.raises(AssertionError):
        builder._makeTravHarvConfigPartFromDict(dict_object, name_config)


def test__makeTravHarvConfigPartFromDict_missing_assert_subjects():
    # Create a test instance of TravHarvConfigBuilder
    test_target_store = TargetStore(
        mode="memory",
        context=["./tests/inputs/63523.ttl"],
    )
    builder = TravHarvConfigBuilder(
        test_target_store,
        config_folder,
    )

    # Define test inputs
    dict_object = {
        "snooze-till-graph-age-minutes": 60,
        "prefix": "prefix",
    }
    name_config = "default"

    # Call the method under test
    with pytest.raises(AssertionError):
        builder._makeTravHarvConfigPartFromDict(dict_object, name_config)


def test__makeTravHarvConfigPartFromDict_missing_assert_paths():
    # Create a test instance of TravHarvConfigBuilder
    test_target_store = TargetStore(
        mode="memory",
        context=["./tests/inputs/63523.ttl"],
    )
    builder = TravHarvConfigBuilder(
        test_target_store,
        config_folder,
    )

    # Define test inputs
    dict_object = {
        "snooze-till-graph-age-minutes": 60,
        "assert": [
            {
                "subjects": {
                    "literal": ["subject1", "subject2"],
                    "SPARQL": "SELECT ?s WHERE { ?s ?p ?o }",
                },
            }
        ],
        "prefix": "prefix",
    }
    name_config = "default"

    # Call the method under test
    with pytest.raises(
        KeyError
    ):  # TODO: check if this is the correct exception
        builder._makeTravHarvConfigPartFromDict(dict_object, name_config)


def test__check_snooze():
    # Create a test instance of TravHarvConfigBuilder
    test_target_store = TargetStore(
        mode="memory",
        context=["./tests/inputs/63523.ttl"],
    )
    builder = TravHarvConfigBuilder(
        test_target_store,
        config_folder,
    )

    # Define test inputs
    snooze_time = 60
    lastmodified_admin = {
        "default": datetime.now() - timedelta(minutes=30),
        "other_config": datetime.now() - timedelta(minutes=90),
    }
    name_config = "default"

    # Call the method under test
    result = builder._check_snooze(
        snooze_time, lastmodified_admin, name_config
    )

    # Perform assertions on the result
    assert isinstance(result, bool)
    assert (
        result is True
    )  # Assuming the current time is within the snooze period

    # Add more assertions as needed


def test__check_snooze_expired():
    # Create a test instance of TravHarvConfigBuilder
    test_target_store = TargetStore(
        mode="memory",
        context=["./tests/inputs/63523.ttl"],
    )
    builder = TravHarvConfigBuilder(
        test_target_store,
        config_folder,
    )

    # Define test inputs
    snooze_time = 60
    lastmodified_admin = {
        "default": datetime.now() - timedelta(minutes=120),
        "other_config": datetime.now() - timedelta(minutes=90),
    }
    name_config = "default"

    # Call the method under test
    result = builder._check_snooze(
        snooze_time, lastmodified_admin, name_config
    )

    # Perform assertions on the result
    assert isinstance(result, bool)
    assert (
        result is False
    )  # Assuming the current time is beyond the snooze period

    # Add more assertions as needed


def test_assert_path():
    # Create a test suite of assertions

    test_paths = [
        {
            "path": "mr:segment_uno/<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>",
            "return_segments": [
                "mr:segment_uno",
                "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>",
            ],
            "return_segments_count": 2,
            "return_segment_path_depth_test": [
                {
                    "size": 2,
                    "segment": "mr:segment_uno/<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>",
                },
            ],
        },
        {
            "path": "ex:test/pr:segment_dos",
            "return_segments": ["ex:test", "pr:segment_dos"],
            "return_segments_count": 2,
            "return_segment_path_depth_test": [
                {
                    "size": 2,
                    "segment": "ex:test/pr:segment_dos",
                },
                {
                    "size": 1,
                    "segment": "ex:test",
                },
            ],
        },
        {
            "path": "<http://blabla.org>/pp:test/ex:lol/<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>/<https://www.w3.org/1999/02/22-rdf-syntax-ns#type>",
            "return_segments": [
                "<http://blabla.org>",
                "pp:test",
                "ex:lol",
                "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>",
                "<https://www.w3.org/1999/02/22-rdf-syntax-ns#type>",
            ],
            "return_segments_count": 5,
            "return_segment_path_depth_test": [
                {
                    "size": 3,
                    "segment": "<http://blabla.org>/pp:test/ex:lol",
                },
                {
                    "size": 4,
                    "segment": "<http://blabla.org>/pp:test/ex:lol/<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>",
                },
            ],
        },
    ]

    for test_path in test_paths:
        # Call the method under test
        result = AssertPath(test_path["path"])

        # Perform assertions on the result
        assert result.get_path_parts() == test_path["return_segments"]
        assert (
            len(result.get_path_parts()) == test_path["return_segments_count"]
        )
        assert result.get_max_size() == test_path["return_segments_count"]

        for depth_test in test_path["return_segment_path_depth_test"]:
            assert (
                result.get_path_for_depth(depth_test["size"])
                == depth_test["segment"]
            )
