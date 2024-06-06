#!/usr/bin/env python
import pytest
from conftest import TEST_CONFIG_FOLDER
from util4tests import run_single_test

from travharv.config_build import TravHarvConfigBuilder
from travharv.executor import TravHarvExecutor


@pytest.mark.usefixtures("decorated_rdf_stores")
def test_travharv_executor(decorated_rdf_stores):
    for rdf_store in decorated_rdf_stores:
        # first make travharv_config_builder
        travharvconfigbuilder = TravHarvConfigBuilder(
            rdf_store,
            str(TEST_CONFIG_FOLDER / "good_folder"),
        )

        travharvobject = travharvconfigbuilder.build_from_config(
            "base_test.yml"
        )

        # extract values from travharvobject and pass them to travharvexecutor
        TravHarvExecutor(
            travharvobject.configname,
            travharvobject.NSM,
            travharvobject.tasks,
            rdf_store,
        ).assert_all_paths()


if __name__ == "__main__":
    run_single_test(__file__)
