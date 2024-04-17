#!/usr/bin/env python
# import pytest
# from rdflib import URIRef
# from rdflib.query import ResultRow
from util4tests import run_single_test

# from travharv.config_build import AssertPath
# from travharv.path_assertion import SubjPropPathAssertion

"""
@pytest.mark.usefixtures("decorated_rdf_stores")
def test_init_subj_prop_path_assertion(decorated_rdf_stores):
    assertion_path = AssertPath("http://example.org/subject")

    for rdf_store in decorated_rdf_stores:
        subj_prop_path_assertion = SubjPropPathAssertion(
            "http://example.org/subject",
            assertion_path,
            rdf_store,
            {},
            "urn:test",
        )
        assert subj_prop_path_assertion.subject == "http://example.org/subject"
        assert subj_prop_path_assertion.assertion_path == assertion_path


@pytest.mark.usefixtures("decorated_rdf_stores")
def test_subject_str_check(decorated_rdf_stores):
    assertion_path = AssertPath("http://example.org/subject")

    for rdf_store in decorated_rdf_stores:
        assertion_path = AssertPath("http://example.org/subject")
        subj_prop_path_assertion = SubjPropPathAssertion(
            "http://example.org/subject",
            assertion_path,
            rdf_store,
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
                ResultRow(
                    {"subject": "http://example.org/subject"}, ["subject"]
                )
            )
            == "http://example.org/subject"
        )

        # test when subject is not uri
        assert (
            subj_prop_path_assertion._subject_str_check("example.org/subject")
            is None
        )
"""

if __name__ == "__main__":
    run_single_test(__file__)
