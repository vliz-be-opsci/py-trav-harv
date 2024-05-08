import logging

import rdflib
import validators
from rdflib.namespace import NamespaceManager
from datetime import datetime
from uuid import uuid4

from travharv.config_build import AssertPath
from travharv.store import RDFStoreAccess
from travharv.web_discovery import get_description_into_graph
from travharv.execution_report import (
    TaskExecutionReport,
    AssertionReport,
)

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
        rdf_store_access: RDFStoreAccess,
        NSM: NamespaceManager,
        config_name: str,
        task_execution_report: TaskExecutionReport,
    ):
        """
        Construct a SubjPropPathAssertion object.
        Automatically asserts a property path for a given subject.
        Puts the results in a RDFStoreAccess.

        :param subject: str
        :param assertion_path: AssertPath
        :param rdf_store_access: RDFStoreAccess
        :param NSM: dict
        :param config_name: str

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
        self.NSM = NSM
        self.config_name = config_name
        self.task_execution_report = task_execution_report
        self.assertion_report_info = {
            "subject_uri": self.subject,
            "id": uuid4(),
        }
        self.bounced = False
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
            if (
                self.current_depth > self.previous_bounce_depth
                and self.previous_bounce_depth != 0
            ):
                self.assertion_report_info["assertion_path"] = (
                    self.assertion_path.get_path_for_depth(
                        self.max_depth - self.current_depth
                    )
                )
                self.assertion_report_info["assertion_time"] = datetime.now()
                self.assertion_report_info["assertion_result"] = False
                assertion_report = AssertionReport(
                    subject_uri=self.subject,
                    assertion_path=self.assertion_report_info[
                        "assertion_path"
                    ],
                    assertion_result=self.assertion_report_info[
                        "assertion_result"
                    ],
                    assertion_time=self.assertion_report_info[
                        "assertion_time"
                    ],
                    id=self.assertion_report_info["id"],
                    download_url=None,
                    rdf_store_access=self.rdf_store_access,
                    triple_count=None,
                    document_type=None,
                )
                self.task_execution_report.report_to_store(assertion_report)
                assertion_report.report_to_store()
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
        log.debug(
            "ppath: {}".format(
                self.assertion_path.get_path_for_depth(
                    self.max_depth - self.current_depth
                )
            )
        )
        if self.rdf_store_access.verify_path(
            self.subject,
            self.assertion_path.get_path_for_depth(
                self.max_depth - self.current_depth
            ),
            self.NSM,
        ):
            self._harvest_and_surface()
            return

        log.debug(
            f"""TODO check config_name to be str now is:
            {type(self.config_name).__name__}."""
        )
        self.assertion_report_info["assertion_path"] = (
            self.assertion_path.get_path_for_depth(
                self.max_depth - self.current_depth
            )
        )

        # if bounced then the download url should change to the subject so it can be harvested
        if self.bounced:
            log.debug(f"bounced_subject: {self.bounced_subject}")
            self.bounced_subject = (
                self.subject
            )  # TODO this is not the correct bounced subject redo this logic so that this is the correct subject
            # TODO find a way to check if all can be covered to until a full PP is dereferenced

        get_description_into_graph(
            subject_url=self.bounced_subject if self.bounced else self.subject,
            store=self.rdf_store_access,
            config_file=self.config_name,
            assertion_report_info=self.assertion_report_info,
            task_execution_report=self.task_execution_report,
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
        self.bounced = True
