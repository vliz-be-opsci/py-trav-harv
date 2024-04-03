import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from util4tests import run_single_test

from travharv import TravHarv

load_dotenv()

read_uri = os.getenv("TEST_SPARQL_READ_URI")
write_uri = os.getenv("TEST_SPARQL_WRITE_URI")

"""
def test_travharv():
    config_folder = Path(__file__).parent / "config"
    name = "config_sparql_uri_string_fail.yml"
    output = Path(__file__).parent / "output" / "output_wrong_uri.ttl"
    target_store_info = [read_uri, write_uri]
    verbose = True

    travharv = TravHarv(
        config_folder,
        name,
        output,
        None,
        target_store_info,
        verbose,
    )

    print(travharv.target_store_access.__str__)

    travharv.process()

    assert travharv is not None
    assert True

    # check if output.ttl exist and is not empty and == test_output.ttl

    assert os.path.exists(
        Path(__file__).parent / "output" / "output_wrong_uri.ttl"
    )
    assert (
        os.path.getsize(
            Path(__file__).parent / "output" / "output_wrong_uri.ttl"
        )
        > 0
    )
"""


def test_travharv_fail():
    config_folder = Path(__file__).parent / "config"
    name = " bad_config.yml"
    output = Path(__file__).parent / "output" / "output.ttl"
    target_store_info = [read_uri, write_uri]
    verbose = True

    travharv = TravHarv(
        config_folder,
        name,
        output,
        None,
        target_store_info,
        verbose,
    )

    with pytest.raises(Exception):
        travharv.process()


def test_travharv_config_folder_fail():
    config_folder = Path(__file__).parent / "config"
    target_store_info = [read_uri, write_uri]
    verbose = True

    travharv = TravHarv(
        config_folder,
        None,
        None,
        None,
        target_store_info,
        verbose,
    )

    with pytest.raises(Exception):
        travharv.process()


if __name__ == "__main__":
    run_single_test(__file__)