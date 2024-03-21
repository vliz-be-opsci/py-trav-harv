import pytest
from util4tests import run_single_test
import os
from pathlib import Path
from pytravharv import TravHarv
from rdflib import Graph
from dotenv import load_dotenv

load_dotenv()

read_uri = os.getenv("TEST_SPARQL_READ_URI")
write_uri = os.getenv("TEST_SPARQL_WRITE_URI")


def test_pytravharv():
    config_folder = Path(__file__).parent / "config"
    name = "base_test.yml"
    output = "output"
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


if __name__ == "__main__":
    run_single_test(__file__)
