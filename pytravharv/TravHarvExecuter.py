from pytravharv.SubjPropPathAssertion import SubjPropPathAssertion
from pytravharv.TargetStore import TargetStore
from pytravharv.TravHarvConfigBuilder import (
    LiteralSubjectDefinition,
    PrefixSet,
    SPARQLSubjectDefinition,
)
import logging

log = logging.getLogger("pyTravHarv")


class TravHarvExecutor:
    """
    A class to represent a TravHarvExecutor.
    This class will assert all paths for all subjects given for each task per config.
    """

    def __init__(
        self,
        config_filename: str,
        prefix_set: PrefixSet,
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
            info_task = task.get_task()
            log.debug("Info task: {}".format(info_task))
            subject_definition = info_task["subject_definition"]
            assertion_path_set = info_task[
                "assert_path_set"
            ].get_assert_path_set()
            for subject in self._define_subjects(subject_definition):
                log.debug("Subject: {}".format(subject))
                for assertion_path in assertion_path_set:
                    SubjPropPathAssertion(
                        subject,
                        assertion_path,
                        self.target_store,
                        self.prefix_set,
                        self.config_filename,
                    )

    def _define_subjects(self, subject_definition):
        """
        Define subjects to assert paths for.
        """
        log.debug("Defining subjects to assert paths for")
        # Implement method to define subjects to assert paths for
        if (
            type(subject_definition.get_subject_definition())
            == LiteralSubjectDefinition
        ):
            log.debug("LiteralSubjectDefinition")
            # assert all paths
            return subject_definition.get_subject_definition().get_subjects()
        if (
            type(subject_definition.get_subject_definition())
            == SPARQLSubjectDefinition
        ):
            log.debug("SPARQLSubjectDefinition")
            log.debug(
                "SPARQL query: {}".format(
                    subject_definition.get_subject_definition().get_subjects()
                )
            )
            return self.target_store.target_store.select_subjects(
                subject_definition.get_subject_definition().get_subjects()
            )
