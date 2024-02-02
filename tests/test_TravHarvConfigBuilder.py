import pytest
from pyTravHarv.TravHarvConfigBuilder import (
    TravHarvConfigBuilder,
    PrefixSet,
    LiteralSubjectDefinition,
    SPARQLSubjectDefinition,
    SubjectDefinition,
    AssertPath,
    AssertPathSet,
    TravHarvTask,
)
import os

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
