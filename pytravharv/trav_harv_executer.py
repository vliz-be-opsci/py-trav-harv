import logging
from typing import Optional

from rdflib import Graph

from pytravharv.store import TargetStoreAccess
from pytravharv.subj_prop_path_assertion import SubjPropPathAssertion
from pytravharv.trav_harv_config_builder import TravHarvConfig

# log = logging.getLogger("pyTravHarv")
log = logging.getLogger(__name__)


class TravHarvExecutor:
    """
    A class to represent a TravHarvExecutor.
    This class will assert all paths for all subjects given for each task per config.

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
        output: Optional[str] = None,
    ):
        self.config_filename = config_filename
        self.prefix_set = prefix_set
        self.tasks = tasks
        self.rdf_store_access = rdf_store_access
        self.output = output
        log.debug("TravHarvExecutor initialized")
        log.debug("Config filename: {}".format(self.config_filename))
        log.debug("Prefix set: {}".format(self.prefix_set))
        log.debug("Tasks: {}".format(self.tasks))

    def assert_all_paths(self):
        """
        Assert all paths for all subjects given for each task per config.
        """
        log.debug(
            "Asserting all paths for all subjects given for each task per config"
        )
        for task in self.tasks:
            log.debug("Task: {}".format(task))
            # check if subject is a URI or a SPARQL query
            log.debug("Info task: {}".format(task))
            subject_definition = task.subject_definition
            assertion_path_set = task.assert_path_set
            print("Subject definition: {}".format(subject_definition()))
            log.debug("Subject definition: {}".format(subject_definition))
            print("Assertion path set: {}".format(assertion_path_set()))
            log.debug("Assertion path set: {}".format(assertion_path_set))
            for subject in subject_definition():
                log.debug("Subject: {}".format(subject))
                for assertion_path in assertion_path_set():
                    log.debug("Assertion path: {}".format(str(assertion_path)))
                    print("Assertion path: {}".format(str(assertion_path)))
                    SubjPropPathAssertion(
                        subject,
                        assertion_path,
                        self.rdf_store_access,
                        self.prefix_set,
                        self.config_filename,
                    )
            log.debug("All paths asserted for task: {}".format(task))
            if self.output:
                log.debug("Output to file: {}".format(self.output))
                # write graph to file
                full_graph = self.rdf_store_access.full_graph()
                # log.debug("Full graph: {}".format(full_graph))
                # go from list of tuples to graph
                output_graph = Graph()
                if full_graph:
                    for triple in full_graph:
                        output_graph.add(triple)
                    output_graph.serialize(self.output, format="turtle")
            else:
                log.debug("No output file specified")
