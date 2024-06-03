#!/usr/bin/env python
import logging
from pathlib import Path

import pytest
from conftest import TEST_Path
from pyrdfj2 import J2RDFSyntaxBuilder
from util4tests import run_single_test

from travharv import TravHarv

log = logging.getLogger(__name__)

QUERY_BUILDER: J2RDFSyntaxBuilder = J2RDFSyntaxBuilder(
    templates_folder=str(Path(__file__).parent / "scenarios" / "templates")
)

BASE = "http://localhost:8080/"
OUTPUTS = TEST_Path / "output"
INPUT = TEST_Path / "input"
CONFIGS = TEST_Path / "travharv_config"
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


@pytest.mark.usefixtures("httpd_server_base", "store_info_sets")
def test_scenario_one(
    httpd_server_base: str,
    store_info_sets,
):
    assert httpd_server_base
    for store in store_info_sets:
        log.debug(f"testing scenario one for {store}")
        config = CONFIGS / "dereference_test1_sparql.yml"
        travharv = TravHarv(
            config,
            store,
        )

        travharv.process()

        # assertions here


@pytest.mark.usefixtures("httpd_server_base", "store_info_sets")
def test_scenario_two(
    httpd_server_base: str,
    store_info_sets,
):
    assert httpd_server_base
    for store in store_info_sets:
        log.debug(f"testing scenario one for {store}")
        config = CONFIGS / "dereference_test2_sparql.yml"
        travharv = TravHarv(
            config,
            store,
        )
        travharv.process()
        # assertions here


@pytest.mark.usefixtures("httpd_server_base", "store_info_sets")
def test_scenario_tree(
    httpd_server_base: str,
    store_info_sets,
):
    assert httpd_server_base
    for store in store_info_sets:
        log.debug(f"testing scenario one for {store}")
        config = CONFIGS / "dereference_test3_sparql.yml"
        travharv = TravHarv(
            config,
            store,
        )
        travharv.process()
        # assertions here


@pytest.mark.usefixtures("httpd_server_base", "store_info_sets")
def test_scenario_four(
    httpd_server_base: str,
    store_info_sets,
):
    assert httpd_server_base
    for store in store_info_sets:
        log.debug(f"testing scenario one for {store}")
        config = CONFIGS / "dereference_test4_sparql.yml"
        travharv = TravHarv(
            config,
            store,
        )
        travharv.process()
        # assertions here


@pytest.mark.usefixtures("httpd_server_base", "store_info_sets")
def test_scenario_five(
    httpd_server_base: str,
    store_info_sets,
):
    assert httpd_server_base
    for store in store_info_sets:
        log.debug(f"testing scenario one for {store}")
        config = CONFIGS / "dereference_test5_sparql.yml"
        travharv = TravHarv(
            config,
            store,
        )
        travharv.process()
        # assertions here


"""
# launch a server with subprocess from local_server.py
@pytest.mark.usefixtures("httpd_server_base", "store_info_sets")
def test_scenarios(
    httpd_server_base: str,
    store_info_sets,
):
    assert httpd_server_base
    for store_info in store_info_sets:
        for config in CONFIGS.glob("*.yml"):
            if config.name not in SCENARIOS_OUTCOMES:
                log.debug(
                    f"Skipping scenario {config}"
                    f" as it is not present in"
                    f" SCENARIOS_OUTCOMES"
                )
                continue
            for test_case in SCENARIOS_OUTCOMES[config.name]:
                mode = test_case["mode"]
                log.debug(f"{mode=}")

                # TODO: when mode is added in 0.0.5 add tests here
                # for now continue

                if mode == "nostop":
                    log.debug(
                        f"Skipping scenario {config} with mode {mode}"
                        f" as it is not yet implemented"
                    )
                    continue

                log.debug(f"Running scenario {config} with store {store_info}")
                travharv = TravHarv(
                    config,
                    store_info,
                )
                travharv.process()
                # assert travharv.error_occurred
                # other assertions here based on the scenarios

                # get the context name for the config name
                context_name_graph = travharv.target_store._nmapper.key_to_ng(
                    config.name
                )
                log.debug(f"{context_name_graph=}")

                # make sparql for the test
                sparql = QUERY_BUILDER.build_syntax(
                    "execution_report_data.sparql",
                    context_name_graph=context_name_graph,
                )

                log.debug(f"{store_info=}")

                if store_info == ():
                    sparql = QUERY_BUILDER.build_syntax(
                        "execution_report_data.sparql",
                    )
                    execution_report_data_result = (
                        travharv.target_store.select(sparql)
                    )
                    sparql_all = "SELECT ?s ?p ?o WHERE { ?s ?p ?o }"
                else:
                    execution_report_data_result = (
                        travharv.target_store.select(sparql)
                    )
                    sparql_all = (
                        f"SELECT ?s ?p ?o FROM <{context_name_graph}> "
                        f"WHERE {{ ?s ?p ?o }}"
                    )

                all_triples = travharv.target_store.select(sparql_all)
                # get length of the result
                log.debug(f"{len(execution_report_data_result)=}")
                log.debug(f"{len(all_triples)=}")
                netto_triples = len(all_triples) - len(
                    execution_report_data_result
                )
                log.debug(f"{netto_triples=}")

                # delete the context from the store so
                # # it doesn't interfere with the next test
                travharv.target_store.drop_graph_for_config(config.name)

                # assert to see if the netto_triples is
                # the same as the expected_len_triples
                # assert netto_triples == int(test_case["expected_len_triples"])
"""

if __name__ == "__main__":
    run_single_test(__file__)
