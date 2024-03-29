# from rdflib.plugins.sparql.parser import parseQuery #this line is commented out because pytest has an issue with this import specifically
import re
import os
import sys
from typing import Any
import yaml
import logging
from datetime import datetime, timedelta
from pytravharv.TargetStore import TargetStore
from rdflib.plugins.sparql.parser import parseQuery
from abc import ABC, abstractmethod

# log = logging.getLogger("pyTravHarv")
log = logging.getLogger(__name__)


class TravHarvTask:
    """
    A task for the travharv
    This task contains the following:
    - SubjectDefinition class: a class that defines the subjects
    - AssertPathSet class: a class that contains a list of AssertPath objects
    """

    def __init__(self, task):
        """
        Initialise the task

        :param task: The task.
        :type task: dict
        """
        self.task = task

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.task

    @property
    def subject_definition(self):
        return self.task["subject_definition"]

    @property
    def assert_path_set(self):
        return self.task["assert_path_set"]


class SubjectDefinition(ABC):
    @abstractmethod
    def listSubjects(self) -> list[str]:
        pass

    @abstractmethod
    def __call__(self, *args: Any, **kwds: Any) -> list[str]:
        pass


class LiteralSubjectDefinition(SubjectDefinition):
    """
    A subject definition that is a list of strings
    """

    def __init__(self, subjects):
        """
        Initialise the literal subject definition

        :param subjects: The subjects.
        :type subjects: list[str]
        """
        self.subjects = subjects

    def __call__(self, *args: Any, **kwds: Any) -> list[str]:
        log.debug(self.subjects)
        return self.subjects

    def listSubjects(self) -> list[str]:
        """
        Get the subjects

        :return: list[str]
        :rtype: list[str]
        """
        return self.subjects


class SPARQLSubjectDefinition(SubjectDefinition):
    """
    A subject definition that is a SPARQL query
    """

    def __init__(self, SPARQL=str, targetstore=TargetStore):
        """
        Initialise the SPARQL subject definition

        :param SPARQL: The SPARQL query.
        :type SPARQL: str
        :param targetstore: The target store.
        :type targetstore: TargetStore
        """
        log.debug("init SPARQL subjects")
        self.subjects = self._get_subjects(SPARQL, targetstore)
        log.debug(self.subjects)

    def __call__(self, *args: Any, **kwds: Any) -> list[str]:
        return self.subjects

    def listSubjects(self) -> list[str]:
        """
        Get the subjects

        :return: list[str]
        :rtype: list[str]
        """
        return self.subjects

    def _get_subjects(self, SPARQL=str, targetstore=TargetStore):
        log.debug("getting subjects")
        return targetstore().select_subjects(SPARQL)


class AssertPathSet:
    """
    A set/list of assert paths
    """

    def __init__(self, assert_path_set):
        """
        Initialise the assert path set

        :param assert_path_set: The set of assert paths.
        :type assert_path_set: list[AssertPath]
        """
        self.assert_path_set = assert_path_set

    def __call__(self):
        """
        Get the assert path set
        """
        return self.assert_path_set


class AssertPath:
    """
    A path to assert.
    This class contains the following:
    - Path_parts: a list of strings
    - max_size: a function to return the len of the list of path_parts
    - get_path_for_depth(): a function that returns a path at a given depth
    """

    def __init__(self, assert_path=str):
        """
        Initialise the assert path

        :param assert_path: The path to assert.
        :type assert_path: str
        """
        self.path_parts = self._make_path_parts(assert_path)

    def __str__(self) -> str:
        return "/".join(self.path_parts)

    def get_path_parts(self):
        """
        Get the path parts

        return: list[str]
        rtype: list[str]
        """
        return self.path_parts

    def get_max_size(self):
        """
        Get the max size

        return: int
        rtype: int
        """
        return len(self.path_parts)

    def get_path_for_depth(self, depth):
        """
        Get a concatination of the path parts up to a given depth

        return: str
        rtype: str
        """
        return "/".join(self.path_parts[:depth])

    def _make_path_parts(self, assert_path):
        """
        Make the path parts by splitting the path string on regex expression
        """
        REGEXP = r"(?:\w+:\w+|<[^>]+>)"

        # split the path on the regex expression
        return re.findall(REGEXP, assert_path)


class TravHarvConfig:
    """
    Configuration for the travharv
    This class contains the following:
        - PrefixSet: a dictionary of prefixes
        - tasks: a list of tasks
        - ConfigName: a string
    """

    def __init__(self, travharv_config):
        """
        Initialise the travharv config.

        :param travharv_config: The configuration for the travharv config.
        :type travharv_config: dict
        :return: A TravHarvConfig object.
        :rtype: TravHarvConfig
        """
        self.travharv_config = travharv_config

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.travharv_config

    @property
    def PrefixSet(self):
        return self.travharv_config["PrefixSet"]

    @property
    def tasks(self):
        return self.travharv_config["tasks"]

    @property
    def ConfigName(self):
        return self.travharv_config["ConfigName"]

    def __str__(self):
        return str(self.travharv_config)


class TravHarvConfigBuilder:
    def __init__(self, target_store: TargetStore, configFolder: str = None):
        """
        Initialize the TravHarvConfigBuilder.

        :param target_store: The target store for the TravHarvConfigBuilder.
        :type target_store: TargetStore
        :param configFolder: The folder containing the config files.
        :type configFolder: str
        :return: A TravHarvConfigBuilder object.
        :rtype: TravHarvConfigBuilder
        """
        if configFolder is None:
            configFolder = os.path.join(os.getcwd(), "config")
            log.warning(
                "Config folder is None, using current working directory as config folder"
            )
        self.config_files_folder = configFolder
        self.target_store = target_store
        self.lastmodified_admin = target_store().lastmod()
        log.debug(self.lastmodified_admin)
        log.debug("TravHarvConfigBuilder initialized")

    def build_from_config(self, config_name):
        """
        Build a TravHarvConfig from a given config file.

        :param config_name: The name of the config file.
        :type config_name: str
        :return: A TravHarvConfig object.
        :rtype: TravHarvConfig
        """
        config_file = os.path.join(self.config_files_folder, config_name)
        dict_object = self._load_yml_to_dict(config_file)
        return self._makeTravHarvConfigPartFromDict(dict_object, config_name)

    def build_from_folder(self):
        """
        Build a list of TravHarvConfig objects from a given folder.

        :return: A list of TravHarvConfig objects.
        :rtype: list[TravHarvConfig]
        """
        config_files = self._files_folder()
        configs = []
        for config_file in config_files:
            path_config_file = os.path.join(
                self.config_files_folder, config_file
            )
            dict_object = self._load_yml_to_dict(path_config_file)
            configs.append(
                self._makeTravHarvConfigPartFromDict(dict_object, config_file)
            )
        return configs

    def _assert_subjects(self, subjects):
        assert isinstance(subjects, dict), "Subjects must be a dictionary"
        assert (
            "literal" in subjects or "SPARQL" in subjects
        ), "Subjects must contain 'literal' or 'SPARQL'"
        for key, value in subjects.items():
            if key == "literal":
                assert isinstance(
                    value, list
                ), "Subjects of type literal must be a list of strings"
                for subject in value:
                    assert isinstance(
                        subject, str
                    ), "Subjects of type literal must be a list of strings"
            if key == "SPARQL":
                assert isinstance(
                    value, str
                ), "Subjects of type SPARQL must be a string"
                self._assert_valid_sparql_syntax(value)
        # Add more assertions as needed...

    def _assert_valid_sparql_syntax(self, sparql_query):
        parseQuery(sparql_query)
        assert isinstance(sparql_query, str), "SPARQL query must be a string"
        # Add more assertions as needed...

    def _files_folder(self):
        return [
            f
            for f in os.listdir(self.config_files_folder)
            if f.endswith((".yml", ".yaml"))
        ]

    def _load_yml_to_dict(self, file):
        with open(file, "r") as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def _makeTravHarvConfigPartFromDict(
        self, dict_object, name_config="default"
    ):

        # make it so that the assertions are always checked for lowercase
        dict_object = {k.lower(): v for k, v in dict_object.items()}
        assert (
            "snooze-till-graph-age-minutes" in dict_object
        ), "snooze-till-graph-age-minutes must be defined"
        assert "assert" in dict_object, "assert must be defined"
        for assert_task in dict_object["assert"]:
            self._assert_subjects(assert_task["subjects"])
        # Add more assertions as needed...

        # function here to check if the snooze-till-graph-age-minutes i older then the last modified date of the admin graph
        # if it is older then the last modified date of the admin graph then we can continue
        # if it is not older then the last modified date of the admin graph then we can snooze the config
        if self._check_snooze(
            dict_object["snooze-till-graph-age-minutes"],
            self.lastmodified_admin,
            name_config,
        ):
            log.info(
                "Snoozing config {} for {} minutes".format(
                    name_config, dict_object["snooze-till-graph-age-minutes"]
                )
            )
            return

        travharvconfig = {
            "ConfigName": name_config,
            "PrefixSet": dict_object["prefix"],
            "tasks": [
                TravHarvTask(
                    {
                        "subject_definition": (
                            LiteralSubjectDefinition(
                                assert_task["subjects"]["literal"]
                            )
                            if "literal" in assert_task["subjects"]
                            else SPARQLSubjectDefinition(
                                assert_task["subjects"]["SPARQL"],
                                self.target_store,
                            )
                        ),
                        "assert_path_set": AssertPathSet(
                            [AssertPath(path) for path in assert_task["paths"]]
                        ),
                    }
                )
                for assert_task in dict_object["assert"]
            ],
        }

        return TravHarvConfig(travharvconfig)

    def _check_snooze(self, snooze_time, lastmodified_admin, name_config):
        if name_config in lastmodified_admin:
            lastmodified_admin_time = lastmodified_admin[name_config]
            log.debug(
                "lastmodified_admin_time: {}".format(lastmodified_admin_time)
            )
            tosnooze_time = lastmodified_admin_time + timedelta(
                minutes=snooze_time
            )

            log.debug("tosnooze_time: {}".format(tosnooze_time))

            if tosnooze_time > datetime.now():
                return True
            else:
                return False
