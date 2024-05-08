from travharv.store import RDFStoreAccess
from datetime import datetime
from uuid import uuid4
import logging

log = logging.getLogger(__name__)


class AssertionReport:
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
        download_url: str,
        rdf_store_access: RDFStoreAccess,
        triple_count: int = None,
        document_type: str = None,
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
        self.id = id
        self.triple_count = triple_count
        self.document_type = document_type
        self.download_url = download_url
        self.rdf_store_access = rdf_store_access
        log.debug("AssertionReport initialized")

    def report_to_store(self):
        """
        Report the results of the assertions to the store.
        """
        log.debug("Reporting the results of the assertions to the store")
        log.debug(f"Subject URI: {self.subject_uri}")
        log.debug(f"Assertion Path: {self.assertion_path}")
        log.debug(f"Assertion Result: {self.assertion_result}")
        log.debug(f"Assertion Time: {self.assertion_time}")
        log.debug(f"ID: {self.id}")
        log.debug(f"Triple Count: {self.triple_count}")
        log.debug(f"Document Type: {self.document_type}")
        log.debug(f"Download URL: {self.download_url}")

        # TODO: write template for reporting triples to store with the report_content


class TaskExecutionReport:
    """
    A class to represent a TaskExecutionReport.
    This class will report the results of the assertions per task.
    e.g.: All AssertionReports will be stored in a dictionary
    """

    def __init__(
        self,
        rdf_store_access: RDFStoreAccess,
    ):
        """constructor

        :param task: Task
        """
        log.debug("TaskExecutionReport initialized")
        self.report_content = {
            "task_id": uuid4(),
            "last_mod": datetime.now(),
        }
        self.rdf_store_access = rdf_store_access

    def report_to_store(self, assertion_report: AssertionReport):
        """
        Report the results of the assertions to the store.
        """
        log.debug("Reporting the results of the assertions to the store")
        assertion_report_id = assertion_report.id
        last_mod = assertion_report.assertion_time

        log.debug(f"Assertion Report ID: {assertion_report_id}")
        log.debug(f"Last Modified: {last_mod}")

        # TODO: write template for adding assertion report to the task report


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

    def report_to_store(self, task_execution_report: TaskExecutionReport):
        """
        Report the results of the assertions to the store.
        """
        log.debug("Reporting the results of the assertions to the store")
        # get info needed for update
        task_id = task_execution_report.report_content["task_id"]
        last_mod = task_execution_report.report_content["last_mod"]

        log.debug(f"Task ID: {task_id}")
        log.debug(f"Last Modified: {last_mod}")
        # TODO: write template for reporting triples to store with the report_content
