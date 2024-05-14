import logging
from datetime import datetime
from typing import List
from uuid import uuid4

from travharv.store import RDFStoreAccess

log = logging.getLogger(__name__)


class GraphAdditionReport:
    """
    A class to represent a GraphAdditionReport.
    This class will report the results of the assertions.
    Contents of this report are :
    - the download url of the document
    - the graph added
    - type of document added : text/turtle or application/ld+json or etc.
    - triple count of the graph added
    """

    def __init__(
        self,
        download_url: str,
        document_type: str,
        triple_count: int,
    ):
        """constructor

        :param download_url: str
        :param graph: str
        :param document_type: str
        :param triple_count: int
        """
        self.download_url = download_url
        self.document_type = document_type
        self.triple_count = triple_count
        self.id = uuid4()
        log.debug("GraphAdditionReport initialized")


class PathAssertionReport:
    """
    A class to represent an AssertionReport.
    This class will report the results of the assertions.
    Contents of this report are :
    - the subject_uri
    - the assertion_path
    - the assertion_result (True or False)
    - the assertion_time
    - id of the assertion (uuid4)
    - triple count of the graph added
    - type of document added : text/turtle or application/ld+json or etc.
    - download url of the document
    """

    def __init__(
        self,
        subject_uri: str,
        assertion_path: str,
        assertion_result: bool,
        assertion_time: datetime,
        id: uuid4,
        message: str = None,
        graph_reports: List[GraphAdditionReport] = [],
    ):
        """constructor

        :param subject_uri: str
        :param assertion_path: str
        :param assertion_result: bool
        :param assertion_time: datetime
        :param uuid: str
        :param triple_count: int
        :param document_type: str
        :param download_url: str
        """

        self.subject_uri = subject_uri
        self.assertion_path = assertion_path
        self.assertion_result = assertion_result
        self.assertion_time = assertion_time
        self.message = message
        self.id = id
        log.debug("AssertionReport initialized")
        self.graph_reports = graph_reports


class TaskExecutionReport:
    """
    A class to represent a TaskExecutionReport.
    This class will report the results of the assertions per task.
    e.g.: All AssertionReports will be stored in a dictionary
    """

    def __init__(
        self,
    ):
        """constructor

        :param task: Task
        """
        log.debug("TaskExecutionReport initialized")
        self.report_content = {
            "task_id": uuid4(),
            "last_mod": datetime.now(),
        }
        self.assertion_reports = []

    def add_path_assertion_report(self, assertion_report: PathAssertionReport):
        """
        Report the results of the assertions to the store.
        """
        log.debug(
            "Reporting the results of the task execution report to the store"
        )
        assertion_report_id = assertion_report.id
        last_mod = assertion_report.assertion_time

        log.debug(f"Assertion Report ID: {assertion_report_id}")
        log.debug(f"Last Modified: {last_mod}")

        self.assertion_reports.append(assertion_report)
        self.report_content["last_mod"] = last_mod


class ExecutionReport:
    """
    A class to represent an ExecutionReport.
    This class will report the results of the assertions per task per config.
    e.g.: All TaskExecutionReports will be stored in a dictionary
    """

    def __init__(self, rdf_store_access: RDFStoreAccess, config_name: str):
        """constructor

        :param rdf_store_access: RDFStoreAccess
        """
        self.rdf_store_access = rdf_store_access
        log.debug("ExecutionReport initialized")
        self.report_content = {
            "last_mod": datetime.now(),
            "config_name": config_name,
        }
        self.task_reports = []

    def add_task_report(self, task_execution_report: TaskExecutionReport):
        """
        Report the results of the assertions to the store.
        """
        log.debug("Reporting the results of the execution report to the store")
        # get info needed for update
        task_id = task_execution_report.report_content["task_id"]
        last_mod = task_execution_report.report_content["last_mod"]

        log.debug(f"Task ID: {task_id}")
        log.debug(f"Last Modified: {last_mod}")

        self.task_reports.append(task_execution_report)
        # TODO: write template for reporting triples
        # to store with the report_content

        log.debug(f"{task_execution_report.report_content['task_id']=}")
        for assertion in task_execution_report.assertion_reports:
            log.debug(f"{assertion.id=}")
            log.debug(f"{assertion.assertion_path=}")
            log.debug(f"{assertion.assertion_result=}")
            log.debug(f"{assertion.message=}")
            log.debug(f"Graphs added: {len(assertion.graph_reports)}")
            # count up the ammount of triples that are
            # located in assertion.graph_reports[i]["triples"]
            c_triples = 0
            for graph in assertion.graph_reports:
                c_triples += graph.triple_count
            log.debug(f"Triples added: {c_triples}")
