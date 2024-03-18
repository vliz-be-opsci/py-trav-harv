import pytest
from rdflib import Graph
from pytravharv.WebAccess import download_uri_to_store


@pytest.mark.usefixtures("target_store")
def test_download_uri_to_store(target_store):
    uri = "https://www.w3.org/People/Berners-Lee/card.ttl"
    download_uri_to_store(uri, target_store)
    query_results = target_store.select("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
    assert len(query_results) > 0
    # Add more assertions as needed
