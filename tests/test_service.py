#!/usr/bin/env python
from pathlib import Path

import pytest
from util4tests import run_single_test

from travharv import TravHarv


@pytest.mark.usefixtures("store_info_sets")
def test_travharv_fail(store_info_sets):
    config = Path(__file__).parent / "config" / "bad_config.yml"

    for store_info in store_info_sets:
        travharv = TravHarv(
            config,
            store_info,
        )

        with pytest.raises(Exception):
            travharv.process()


@pytest.mark.usefixtures("store_info_sets")
def test_travharv_config_folder_fail(store_info_sets):
    config_folder = Path(__file__).parent / "config"
    for store_info in store_info_sets:

        travharv = TravHarv(
            config_folder,
            store_info,
        )

        with pytest.raises(Exception):
            travharv.process()


if __name__ == "__main__":
    run_single_test(__file__)
