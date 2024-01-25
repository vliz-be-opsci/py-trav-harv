import pytest
from pyTravHarv.TravHarvConfigBuilder import TravHarvConfigBuilder
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
