import logging

import rdflib
import validators

from travharv.common import graph_name_to_uri
from travharv.config_build import AssertPath
from travharv.store import TargetStoreAccess
from travharv.web_discovery import get_description_into_graph

# log = logging.getLogger("travharv")
log = logging.getLogger(__name__)


class SubjPropPathAssertion:
    """
    A class to represent the assertion of
    all given property traversal paths for a given subject.
    """

    def __init__(
        self,
        subject: str,
        assertion_path: AssertPath,
        rdf_store_access: TargetStoreAccess,
        prefix_set,
        graph_name: str,
    ):
        """
        Construct a SubjPropPathAssertion object.
        Automatically asserts a property path for a given subject.
        Puts the results in a RDFStoreAccess.

        :param subject: str
        :param assertion_path: AssertPath
        :param rdf_store_access: RDFStoreAccess
        :param prefix_set: dict
        :param graph_name: str

        """
        log.debug(subject)
        self.subject = self._subject_str_check(subject)
        if not self.subject:
            log.warning(
                "Subject is not a valid URIRef or str: {}".format(subject)
            )
            return
        self.assertion_path = assertion_path
        self.current_depth = 0
        self.rdf_store_access = rdf_store_access
        self.previous_bounce_depth = 0
        self.max_depth = self.assertion_path.get_max_size()
        self.prefix_set = prefix_set
        self.graph_name = graph_name
        self.assert_path()

    def _subject_str_check(self, subject):
        """
        Check if subject is a strict str
        , if subject is rdflib.term.URIRef , convert to str
        """
        if type(subject) is str and validators.url(subject):
            log.debug("Subject is a valid URIRef: {}".format(subject))
            return subject
        if (
            type(subject) is rdflib.query.ResultRow
            or type(subject) is rdflib.term.URIRef
        ):
            # extract URIRef from ResultRow
            if type(subject) is rdflib.query.ResultRow:
                subject_row = subject[0]
                if type(subject_row) is dict:
                    subject_row = subject_row[
                        "value"
                    ]  # janky way of getting the URIRef from the ResultRow
                log.debug("Subject row: {}".format(subject_row))
                if validators.url(subject_row):
                    return str(subject_row)
                log.warning(
                    "Subject row is not a URIRef: {}".format(subject_row)
                )
            if validators.url(str(subject)):
                return str(subject)
            log.warning("Subject is not a URIRef: {}".format(subject))
        log.debug("Subject is of type {}".format(type(subject)))
        if not validators.url(str(subject)):
            log.warning("Subject is not a URIRef or a str: {}".format(subject))
            return None

    def assert_path(self):
        """
        Assert a property path for a given subject.
        Put the results in a RDFStoreAccess.
        """
        log.debug("Asserting a property path for a given subject")
        log.debug("Subject: {}".format(self.subject))
        # Implement method to assert a property path for a given subject
        while self.current_depth < self.max_depth:
            if self.current_depth > self.previous_bounce_depth:
                return
            self._assert_at_depth()
            self._increase_depth()

    def _assert_at_depth(self):
        """
        Assert a property path for a given subject at a given depth.
        """
        log.debug(
            "Asserting a property path for a given subject at a given depth"
        )
        log.debug("Depth: {}".format(self.max_depth - self.current_depth))
        if self.rdf_store_access.verify_path(
            self.subject,
            self.assertion_path.get_path_for_depth(
                self.max_depth - self.current_depth
            ),
            self.prefix_set,
        ):
            self._harvest_and_surface()
            return
        self.rdf_store_access.ingest(
            get_description_into_graph(self.subject),
            graph_name_to_uri(self.graph_name),
        )

        # Implement method to assert a property path
        # for a given subject at a given depth

    def _increase_depth(self):
        """
        Increase the depth of the property path assertion.
        """
        log.debug("Increasing the depth of the property path assertion")
        # Implement method to increase the depth of the property path assertion
        self.current_depth += 1

    def _harvest_and_surface(self):
        """
        Harvest the property path and surface back to depth 0.
        """
        log.debug(
            """Harvesting the property path and
               backtracking to the previous depth"""
        )
        # Implement method to harvest the property path
        # and backtrack to the previous depth
        self.previous_bounce_depth = self.current_depth
        self.current_depth = 0
