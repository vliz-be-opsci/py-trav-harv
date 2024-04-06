#!/usr/bin/env python
import os

import pytest
from conftest import TEST_CONFIG_FOLDER
from util4tests import run_single_test

from travharv.config_build import TravHarvConfigBuilder
from travharv.executor import TravHarvExecutor

# TODO seems better to move these to conftest.py
read_uri = os.getenv("TEST_SPARQL_READ_URI")
write_uri = os.getenv("TEST_SPARQL_WRITE_URI")


@pytest.mark.usefixtures("target_store_access")
def test_travharv_executor(target_store_access):
    # first make travharv_config_builder
    travharvconfigbuilder = TravHarvConfigBuilder(
        target_store_access,
        str(TEST_CONFIG_FOLDER / "good_folder"),
    )

    travharvobject = travharvconfigbuilder.build_from_config("base_test.yml")

    # extract values from travharvobject and pass them to travharvexecutor
    TravHarvExecutor(
        travharvobject.configname,
        travharvobject.prefixset,
        travharvobject.tasks,
        target_store_access,
    ).assert_all_paths()


if __name__ == "__main__":
    run_single_test(__file__)
