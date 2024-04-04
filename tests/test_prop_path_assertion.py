import pytest
from rdflib import URIRef
from rdflib.query import ResultRow
from util4tests import run_single_test

import travharv.subj_prop_path_assertion as subj
from travharv.trav_harv_config_builder import AssertPath


@pytest.mark.usefixtures("target_store_access")
def test_init_subj_prop_path_assertion(target_store_access):
    assertion_path = AssertPath("http://example.org/subject")
    subj_prop_path_assertion = subj.SubjPropPathAssertion(
        "http://example.org/subject",
        assertion_path,
        target_store_access,
        {},
        "urn:test",
    )
    assert subj_prop_path_assertion.subject == "http://example.org/subject"
    assert subj_prop_path_assertion.assertion_path == assertion_path


@pytest.mark.usefixtures("target_store_access")
def test_subject_str_check(target_store_access):
    assertion_path = AssertPath("http://example.org/subject")
    subj_prop_path_assertion = subj.SubjPropPathAssertion(
        "http://example.org/subject",
        assertion_path,
        target_store_access,
        {},
        "urn:test",
    )

    assert (
        subj_prop_path_assertion._subject_str_check(
            "http://example.org/subject"
        )
        == "http://example.org/subject"
    )

    # check now when subject is rdflib.query.ResultRow and URIRef

    assert (
        subj_prop_path_assertion._subject_str_check(
            URIRef("http://example.org/subject")
        )
        == "http://example.org/subject"
    )

    assert (
        subj_prop_path_assertion._subject_str_check(
            ResultRow({"subject": "http://example.org/subject"}, ["subject"])
        )
        == "http://example.org/subject"
    )

    # test when subject is not uri
    assert (
        subj_prop_path_assertion._subject_str_check("example.org/subject")
        is None
    )


if __name__ == "__main__":
    run_single_test(__file__)
