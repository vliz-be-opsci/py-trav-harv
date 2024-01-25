import pytest
from pyTravHarv.TravHarvConfigBuilder import TravHarvConfigBuilder


def test_build_from_config():
    builder = TravHarvConfigBuilder("config")
    # Test with a known config name
    config = builder.build_from_config("base_test")
    assert config is not None
    # Test with an unknown config name
    with pytest.raises(SystemExit):
        builder.build_from_config("unknown")


def test_build_from_folder():
    builder = TravHarvConfigBuilder("config")
    builder.build_from_folder()
    # Check that the config object was built
    assert builder.travHarvConfig is not None
    # Check that the config object contains the expected configs
    assert "base_test" in builder.travHarvConfig
    assert "bad_config" not in builder.travHarvConfig
