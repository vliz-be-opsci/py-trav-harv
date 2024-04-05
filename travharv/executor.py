import logging

from rdflib import Graph

from travharv.store import TargetStoreAccess
from travharv.path_assertion import SubjPropPathAssertion
from travharv.config_build import TravHarvConfig

# log = logging.getLogger("travharv")
log = logging.getLogger(__name__)


class TravHarvExecutor:
    """
    A class to represent a TravHarvExecutor.
    This class will assert all paths
    for all subjects given for each task per config.

    :param config_filename: str
    :param prefix_set: dict
    :param tasks: list
    :param rdf_store_access: RDFStoreAccess

    """

    def __init__(
        self,
        config_filename: str,
        prefix_set: TravHarvConfig.prefixset,
        tasks: list,
        rdf_store_access: TargetStoreAccess,
    ):
        self.config_filename = config_filename
        self.prefix_set = prefix_set
        self.tasks = tasks
        self.rdf_store_access = rdf_store_access
        log.debug("TravHarvExecutor initialized")
        log.debug("Config filename: {}".format(self.config_filename))
        log.debug("Prefix set: {}".format(self.prefix_set))
        log.debug("Tasks: {}".format(self.tasks))

    def assert_all_paths(self):
        """
        Assert all paths for all subjects given for each task per config.
        """
        log.debug(
            """Asserting all paths for all
               subjects given for each task per config"""
        )
        output_graph = Graph()
        for task in self.tasks:
            log.debug("Task: {}".format(task))
            # check if subject is a URI or a SPARQL query
            log.debug("Info task: {}".format(task))
            subject_definition = task.subject_definition
            assertion_path_set = task.assert_path_set
            log.debug("Subject definition: {}".format(subject_definition))
            log.debug("Assertion path set: {}".format(assertion_path_set))
            for subject in subject_definition():
                log.debug("Subject: {}".format(subject))
                for assertion_path in assertion_path_set():
                    log.debug("Assertion path: {}".format(str(assertion_path)))
                    SubjPropPathAssertion(
                        subject,
                        assertion_path,
                        self.rdf_store_access,
                        self.prefix_set,
                        self.config_filename,
                    )
            log.debug("All paths asserted for task: {}".format(task))
            full_graph = self.rdf_store_access.full_graph()
            if full_graph:
                for triple in full_graph:
                    output_graph.add(triple)

        log.debug("All paths asserted for all tasks")
        return output_graph
