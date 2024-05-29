#!/usr/bin/env python
import logging
from pathlib import Path

import pytest
import requests
from conftest import TEST_PATH
from pyrdfj2 import J2RDFSyntaxBuilder
from pyrdfstore import RDFStore, create_rdf_store
from rdflib import Graph
from util4tests import run_single_test

from travharv import TravHarv
from travharv.store import RDFStoreAccess

log = logging.getLogger(__name__)

QUERY_BUILDER: J2RDFSyntaxBuilder = J2RDFSyntaxBuilder(
    templates_folder=str(Path(__file__).parent / "scenarios" / "templates")
)

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
    "dereference_test1_sparql.yml": [
        {"expected_len_triples": "19", "mode": "stop"},
        {"expected_len_triples": "19", "mode": "nostop"},
    ],
    "dereference_test2_sparql.yml": [
        {"expected_len_triples": "28", "mode": "stop"},
        {"expected_len_triples": "TBD", "mode": "nostop"},
    ],
    "dereference_test3_sparql.yml": [
        {"expected_len_triples": "19", "mode": "stop"},
        {"expected_len_triples": "TBD", "mode": "nostop"},
    ],
    "dereference_test4_sparql.yml": [
        {"expected_len_triples": "19", "mode": "stop"},
        {"expected_len_triples": "TBD", "mode": "nostop"},
    ],
    "dereference_test5_sparql.yml": [
        {"expected_len_triples": "19", "mode": "stop"},
        {"expected_len_triples": "TBD", "mode": "nostop"},
    ],
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

        g = Graph().parse(url)
        # ttl = g.serialize(format="turtle").strip()
        # log.debug(f"{ttl=}")
        log.debug(f"{len(g)=}")


# launch a server with subprocess from local_server.py
@pytest.mark.usefixtures("httpd_server_base", "store_info_sets")
def test_scenarios(
    httpd_server_base: str,
    store_info_sets,
):
    assert httpd_server_base

    for config in Path(CONFIGS).glob("*.yml"):
        if config.name not in SCENARIOS_OUTCOMES:
            log.debug(f"Skipping scenario {config}")
            continue
        for test_case in SCENARIOS_OUTCOMES[config.name]:
            mode = test_case["mode"]
            log.debug(f"{mode=}")

            # TODO: when mode is added in 0.0.5 add tests here
            # for now continue

            if mode == "nostop":
                log.debug(f"Skipping scenario {config} with mode {mode}")
                continue

            for store_info in store_info_sets:
                log.debug(f"Running scenario {config} with store {store_info}")
                travharv = TravHarv(
                    config,
                    store_info,
                )
                travharv.process()
                # assert travharv.error_occurred
                # other assertions here based on the scenarios

                # make connection with the store
                # create RDF_store
                core_store: RDFStore = create_rdf_store(*store_info)
                rdf_store_access = RDFStoreAccess(core_store)

                # get the context name for the config name
                context_name_graph = rdf_store_access._nmapper.key_to_ng(
                    config.name
                )
                log.debug(f"{context_name_graph=}")

                # make sparql for the test
                sparql = QUERY_BUILDER.build_syntax(
                    "execution_report_data.sparql",
                    context_name_graph=context_name_graph,
                )

                log.debug(f"{store_info=}")

                # if store info is an empty tuple then skip
                if store_info == ():
                    sparql = QUERY_BUILDER.build_syntax(
                        "execution_report_data.sparql",
                    )
                    execution_report_data_result = (
                        travharv.target_store.select(sparql)
                    )
                    sparql_all = "SELECT ?s ?p ?o WHERE { ?s ?p ?o }"
                    all_triples = travharv.target_store.select(sparql_all)
                else:
                    execution_report_data_result = rdf_store_access.select(
                        sparql
                    )
                    sparql_all = (
                        "SELECT ?s ?p ?o FROM <"
                        + context_name_graph
                        + "> \n WHERE { ?s ?p ?o }"
                    )
                    all_triples = rdf_store_access.select(sparql_all)
                # get length of the result
                log.debug(f"{len(execution_report_data_result)=}")
                log.debug(f"{len(all_triples)=}")
                netto_triples = len(all_triples) - len(
                    execution_report_data_result
                )
                log.debug(f"{netto_triples=}")

                # delete the context from the store so
                # # it doesn't interfere with the next test
                rdf_store_access.drop_graph_for_config(config.name)

                # assert to see if the netto_triples is
                # the same as the expected_len_triples
                assert netto_triples == int(test_case["expected_len_triples"])


if __name__ == "__main__":
    run_single_test(__file__)
