#!/usr/bin/env python
import logging

from rdflib import Graph
from util4tests import run_single_test

from travharv.web_discovery import get_graph_for_format

log = logging.getLogger(__name__)

# ttl file
# jsonld file
# html file with ttl file in head as full script
# html file with jsonld file in head as script link
test_cases = [
    {
        "uri": "https://www.w3.org/People/Berners-Lee/card.ttl",
        "length": 86,
        "format": "text/turtle",
    },
    {
        "uri": "https://marineregions.org/mrgid/3293.jsonld",
        "length": 99,
        "format": "application/ld+json",
    },
    {
        "uri": "https://data.arms-mbon.org/",
        "length": 102,
        "format": "text/turtle",
    },
    {
        "uri": "https://data.arms-mbon.org/data_release_001/latest/#",
        "length": 117,
        "format": "application/json",
    },  # add more test cases as needed
]


def test_download_uri_cases():
    for case in test_cases:
        uri = case["uri"]
        format = case["format"]
        log.debug(f"{format}")
        graph = get_graph_for_format(uri, formats=[format])
        assert isinstance(graph, Graph)
        assert len(graph) > 0
        assert len(graph) == case["length"]
        # Add more assertions as needed


if __name__ == "__main__":
    run_single_test(__file__)
