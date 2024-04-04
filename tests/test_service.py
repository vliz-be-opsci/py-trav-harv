import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from util4tests import run_single_test

from travharv import TravHarv

load_dotenv()

read_uri = os.getenv("TEST_SPARQL_READ_URI")
write_uri = os.getenv("TEST_SPARQL_WRITE_URI")


def test_travharv_fail():
    config = Path(__file__).parent / "config" / "bad_config.yml"

    target_store_info = [read_uri, write_uri]

    travharv = TravHarv(
        config,
        target_store_info,
    )

    with pytest.raises(Exception):
        travharv.process()


def test_travharv_config_folder_fail():
    config_folder = Path(__file__).parent / "config"
    target_store_info = [read_uri, write_uri]

    travharv = TravHarv(
        config_folder,
        target_store_info,
    )

    with pytest.raises(Exception):
        travharv.process()


if __name__ == "__main__":
    run_single_test(__file__)
