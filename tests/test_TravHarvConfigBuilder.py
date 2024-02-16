from py import test
from pytravharv import TravHarvConfigBuilder, TargetStore
import os
import pytest

mode = "memory"
config_folder = "./tests/config"
name_good_config = "base_test.yml"
name_bad_config = "bad_config.yml"

test_target_store = TargetStore(
    mode="memory",
    context=["./tests/inputs/63523.ttl"],
)

builder = TravHarvConfigBuilder(
    test_target_store,
    config_folder,
)
