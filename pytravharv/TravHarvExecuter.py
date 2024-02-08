from pytravharv.SubjPropPathAssertion import SubjPropPathAssertion
from pytravharv.TargetStore import TargetStore
from pytravharv.TravHarvConfigBuilder import (
    LiteralSubjectDefinition,
    SPARQLSubjectDefinition,
)
import logging

log = logging.getLogger("pyTravHarv")


class TravHarvExecutor:
    """
    A class to represent a TravHarvExecutor.
    This class will assert all paths for all subjects given for each task per config.

    :param config_filename: str
    :param prefix_set: dict
    :param tasks: list
    :param target_store: TargetStore

    """

    def __init__(
        self,
        config_filename: str,
        prefix_set,
        tasks: list,
        target_store: TargetStore,
    ):
        self.config_filename = config_filename
        self.prefix_set = prefix_set
        self.tasks = tasks
        self.target_store = target_store
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
            log.debug("Subject definition: {}".format(subject_definition))
            log.debug("Assertion path set: {}".format(assertion_path_set))
            for subject in subject_definition():
                log.debug("Subject: {}".format(subject))
                for assertion_path in assertion_path_set():
                    log.debug("Assertion path: {}".format(str(assertion_path)))
                    SubjPropPathAssertion(
                        subject,
                        assertion_path,
                        self.target_store,
                        self.prefix_set,
                        self.config_filename,
                    )
