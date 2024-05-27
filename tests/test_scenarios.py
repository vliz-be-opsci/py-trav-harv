#!/usr/bin/env python
import logging
from pathlib import Path

import pytest
import requests
from conftest import TEST_PATH
from rdflib import Graph
from util4tests import run_single_test

from travharv import TravHarv

log = logging.getLogger(__name__)

BASE = "http://localhost:8080/"
OUTPUTS = TEST_PATH / "output"
INPUT = TEST_PATH / "input"
CONFIGS = TEST_PATH / "travharv_config"
RDF_MIMES = {
    "text/turtle",
    "application/ld+json",
}

# TODO write out all the assertions for the tests
# this being the number of triples
# the documents that ware asserted
SCENARIOS_OUTCOMES = {
    "dereference_test1_sparql.yml": {},
    "dereference_test2_sparql.yml": {},
    "dereference_test3_sparql.yml": {},
    "dereference_test4_sparql.yml": {},
    "dereference_test5_sparql.yml": {},
}


# test if all objects can be retrieved
@pytest.mark.usefixtures("httpd_server_base", "all_extensions_testset")
def test_inputs(httpd_server_base: str, all_extensions_testset):
    assert httpd_server_base

    for input in Path(INPUT).glob("*"):
        log.debug(f"{input=}")
        # get name of file
        name_file = input.name
        url = f"{httpd_server_base}{name_file}"
        log.debug(f"{url=}")
        req = requests.get(url)
        assert req.ok
        ctype = req.headers.get("content-type")
        clen = int(req.headers.get("content-length"))
        assert clen > 0
        log.debug(f"{clen=}")
        log.debug(f"{ctype=}")

        if ctype in RDF_MIMES:
            g = Graph().parse(url)
            ttl = g.serialize(format="turtle").strip()
            log.debug(f"{ttl=}")


# launch a server with subprocess from local_server.py
@pytest.mark.usefixtures("httpd_server_base", "store_info_sets")
def test_scenarios(
    httpd_server_base: str,
    store_info_sets,
):
    assert httpd_server_base

    for config in Path(CONFIGS).glob("*.yml"):
        for store_info in store_info_sets:
            log.debug(f"Running scenario {config} with store {store_info}")
            travharv = TravHarv(
                config,
                store_info,
            )
            travharv.process()
            # assert travharv.error_occurred
            # other assertions here based on the scenarios


if __name__ == "__main__":
    run_single_test(__file__)
