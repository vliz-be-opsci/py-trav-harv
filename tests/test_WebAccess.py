import pytest
from rdflib import Graph
from pytravharv.WebAccess import download_uri_to_store


@pytest.mark.usefixtures("target_store_access")
def test_download_uri_to_graph(target_store_access):
    uri = "https://www.w3.org/People/Berners-Lee/card.ttl"
    graph = Graph()
    download_uri_to_store(uri, graph)
    assert isinstance(graph, Graph)
    assert len(graph) > 0
    target_store_access.ingest(graph, "uri:PYTRAVHARV:base_test.yml")
    query_results = target_store_access.full_graph()
    assert len(query_results) > 0
    assert query_results is not None
    assert len(query_results) == len(graph)

    # Add more assertions as needed


# ttl file
# jsonld file
# html file with ttl file in head as full script
# html file with jsonld file in head as script link
test_cases = [
    {"uri": "https://www.w3.org/People/Berners-Lee/card.ttl", "length": 86},
    {"uri": "https://marineregions.org/mrgid/3293.jsonld", "length": 99},
    {"uri": "https://data.arms-mbon.org/", "length": 102},
    {
        "uri": "https://data.arms-mbon.org/data_release_001/latest/#",
        "length": 115,
    },  # add more test cases as needed
]


def test_download_uri_cases():
    for case in test_cases:
        uri = case["uri"]
        graph = Graph()
        download_uri_to_store(uri, graph)
        assert isinstance(graph, Graph)
        assert len(graph) > 0
        assert len(graph) == case["length"]
        # Add more assertions as needed
