import os

import pytest

from pyTravHarv.TargetStore import (
    MemoryTargetStore,
    TargetStore,
    URITargetStore,
)


def test_get_target_store():
    store_path = "https://example.com/repositories/test"
    target_store = TargetStore(
        store_path
    )  # This test gets halted by validators for some reason
    assert target_store() == target_store.target_store


def test_detect_type_uri_target_store():
    target_store = TargetStore()
    uri_target_store = target_store._detect_type(
        "https://example.com"
    )  # same here
    assert isinstance(uri_target_store, URITargetStore)


def test_detect_type_memory_target_store():
    target_store = TargetStore()
    memory_target_store = target_store._detect_type(
        os.path.join(os.getcwd(), "example.jsonld")
    )
    assert isinstance(memory_target_store, MemoryTargetStore)


def test_detect_type_invalid_target_store():
    target_store = TargetStore()
    with pytest.raises(SystemExit):
        target_store._detect_type("invalid_target_store")


def test_ammount_triples_graph():
    target_store = TargetStore()
    assert target_store._ammount_triples_graph() == len(target_store.graph)


def test_get_target_store():
    target_store = TargetStore()
    assert target_store() == target_store.target_store


def test_detect_type_uri_target_store():
    target_store = TargetStore()
    uri_target_store = target_store._detect_type("https://example.com")
    assert isinstance(uri_target_store, URITargetStore)


def test_detect_type_memory_target_store():
    target_store = TargetStore()
    memory_target_store = target_store._detect_type("/path/to/file")
    assert isinstance(memory_target_store, MemoryTargetStore)


def test_detect_type_invalid_target_store():
    target_store = TargetStore()
    with pytest.raises(SystemExit):
        target_store._detect_type("invalid_target_store")


def test_ammount_triples_graph():
    target_store = TargetStore()
    assert target_store._ammount_triples_graph() == len(target_store.graph)


def test_read_file_in_graph_jsonld():
    target_store = TargetStore()
    target_store.target_store = "example.jsonld"
    target_store._read_file_in_graph()
    assert len(target_store.graph) > 0


def test_read_file_in_graph_ttl():
    target_store = TargetStore()
    target_store.target_store = "example.ttl"
    target_store._read_file_in_graph()
    assert len(target_store.graph) > 0


def test_read_file_in_graph_nt():
    target_store = TargetStore()
    target_store.target_store = "example.nt"
    target_store._read_file_in_graph()
    assert len(target_store.graph) > 0


def test_read_file_in_graph_invalid_extension():
    target_store = TargetStore()
    target_store.target_store = "example.txt"
    with pytest.raises(Exception):
        target_store._read_file_in_graph()


def test_create_graph_valid_file():
    target_store = TargetStore()
    target_store.target_store = "example.jsonld"
    target_store._create_graph()
    assert len(target_store.graph) > 0


def test_create_graph_invalid_file():
    target_store = TargetStore()
    target_store.target_store = "invalid_file.txt"
    with pytest.raises(SystemExit):
        target_store._create_graph()


def test_create_graph_unsupported_format():
    target_store = TargetStore()
    target_store.target_store = "example.txt"
    with pytest.raises(SystemExit):
        target_store._create_graph()


def test_context_2_urn():
    target_store = TargetStore()
    context = "example_context"
    expected_urn = "urn:PYTRAVHARV:example_context"
    assert target_store._context_2_urn(context) == expected_urn
