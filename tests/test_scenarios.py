#!/usr/bin/env python
from pathlib import Path

import pytest
from conftest import TEST_SCENARIOS_FOLDER
from util4tests import log, run_single_test
import logging

from travharv import TravHarv

log = logging.getLogger(__name__)

BASE = "http://localhost:8080/"
INPUTS = TEST_SCENARIOS_FOLDER / "input"
OUTPUTS = TEST_SCENARIOS_FOLDER / "output"
CONFIGS = TEST_SCENARIOS_FOLDER / "travharv_config"

# launch a server with subprocess from local_server.py


@pytest.mark.usefixtures("store_info_sets")
def test_scenarios(store_info_sets):
    config = Path(__file__).parent / "config" / "base_test.yml"
    for config in Path(CONFIGS).glob("*.yml"):
        log.debug(f"Running scenario {config}")
        for store_info in store_info_sets:
            log.debug(f"Running scenario {config} with store {store_info}")
            travharv = TravHarv(
                config,
                store_info,
            )

            travharv.process()
            assert travharv.error_occurred
