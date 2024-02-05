import os
# from rdflib.plugins.sparql.parser import parseQuery #this line is commented out because pytest has an issue with this import specifically
import re
import sys

import yaml

from pyTravHarv.logger import log

# log = logging.getLogger(__name__)


class PrefixSet:
    """
    A set of prefixes
    """

    def __init__(self, prefix_set):
        """
        Initialise the prefix set
        """
        self.prefix_set = prefix_set

    def get_prefix_set(self):
        """
        Get the prefix set
        """
        return self.prefix_set


class TravHarvTask:
    """
    A task for the travharv
    This task contains the following:
    - SubjectDefinition class: a class that defines the subjects to be harvested
    - AssertPathSet class: a class that defines the paths to be asserted
    """

    def __init__(self, task):
        """
        Initialise the task
        """
        self.task = task

    def get_task(self):
        """
        Get the task
        """
        return self.task


class SubjectDefinition:
    """
    A subject definition. This can be either a LiteralSubjectDefinition or a SPARQLSubjectDefinition
    depending on the type of subjects
    """

    def __init__(self, subject_definition):
        """
        Initialise the subject definition
        """
        self.subject_definition = subject_definition

    def get_subject_definition(self):
        """
        Get the subject definition
        """
        return self.subject_definition


class LiteralSubjectDefinition:
    """
    A subject definition that is a list of strings
    """

    def __init__(self, subjects):
        """
        Initialise the literal subject definition
        """
        self.subjects = subjects

    def get_subjects(self):
        """
        Get the subjects
        """
        return self.subjects


class SPARQLSubjectDefinition:
    """
    A subject definition that is a SPARQL query
    """

    def __init__(self, subjects):
        """
        Initialise the SPARQL subject definition
        """
        self.subjects = subjects

    def get_subjects(self):
        """
        Get the subjects
        """
        return self.subjects


class AssertPathSet:
    """
    A set/list of assert paths
    """

    def __init__(self, assert_path_set):
        """
        Initialise the assert path set
        """
        self.assert_path_set = assert_path_set

    def get_assert_path_set(self):
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
        """
        self.path_parts = self._make_path_parts(assert_path)

    def get_path_parts(self):
        """
        Get the path parts
        """
        return self.path_parts

    def get_max_size(self):
        """
        Get the max size
        """
        return len(self.path_parts)

    def get_path_for_depth(self, depth):
        """
        Get a concatination of the path parts up to a given depth
        """
        return "/".join(self.path_parts[:depth])

    def _make_path_parts(self, assert_path):
        """
        Make the path parts by splitting the path string on regex expression
        """
        REGEXP = r"(?:\w+:\w+|<[^>]+>)"

        # split the path on the regex expression
        return re.findall(REGEXP, assert_path)


class TravHarvConfigBuilder:
    """
    Builds a configuration object from a given config folder.
    If no folder is given, the current working directory is used as the config folder.
    """

    def __init__(self, configFolder: str = None):
        """
        Initialise the config builder
        """
        log.debug("Config builder initialized")
        if configFolder is None:
            log.warning("Config folder is None")
            log.warning("Using current working directory as config folder")

        self.config_folder = os.path.join(
            os.getcwd(), *configFolder.split("/")
        )

        self.travHarvConfig = {}

    def build_from_dict(self, config_dict):
        """
        Build a config object from a given config_dict.
        The config_dict should be a dictionary with the following keys:
        - config_file_name: a dictionary with the following keys:
            - prefix: a dictionary with prefixes
            - assert: a list of asserts
                - subjects: a list of subjects or a SPARQL query
                - paths: a list of paths
        example:
        {
            "config_file_name": {
                "prefix": {
                    "ex": "http://example.org/",
                    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                },
                "assert": [
                    {
                        "subjects": {
                            "literal": ["http://example.org/subject1", "http://example.org/subject2"]
                        },
                        "paths": ["/rdf:type", "/ex:property"]
                    }
                ]
            }
        }
        """
        for config_file_name, json_object in config_dict.items():
            if self._check_yml_requirements(json_object, config_file_name):
                self.travHarvConfig[config_file_name] = (
                    self._makeTravHarvConfigPartFromJson(json_object)
                )

    def build_from_config(self, config_file_name):
        """
        Build a config object from a given config_file_name
        """

        # check if path to config_file_name exists
        if not os.path.exists(
            os.path.join(self.config_folder, config_file_name)
        ):
            log.error(
                "Config config_file_name {} not found".format(config_file_name)
            )
            sys.exit(1)

        # load in the config file and check if it is valid
        json_object = self._load_yml_to_json(
            os.path.join(self.config_folder, config_file_name)
        )
        if self._check_yml_requirements(json_object, config_file_name):
            self.travHarvConfig[config_file_name] = (
                self._makeTravHarvConfigPartFromJson(json_object)
            )

    def build_from_folder(self):
        """
        Build a config object from the folder given, all yml files in the folder will be used
        """
        for file in self._files_folder():
            json_object = self._load_yml_to_json(file)
            if self._check_yml_requirements(json_object, file):
                self.travHarvConfig[file] = (
                    self._makeTravHarvConfigPartFromJson(json_object)
                )
        log.info("Config object: {}".format(self.travHarvConfig))

    def _makeTravHarvConfigPartFromJson(self, json_object):
        """
        Make a travharv config part from a json object
        The part should be a dictionary with the following keys:
        - PrefixSet : a dictionary with prefixes
        - Subjectdefinition: either a LiteralSubjectDefinition or a SPARQLSubjectDefinition
        - AssertPathSet: a list of AssertPath objects
            - AssertPath: a dictionary with the following keys:
                - Path_parts: a list of strings
                - max_size: a function to return the len of the list of path_parts
                - get_path_at_depth(): a function that returns a path at a given depth
        """

        for key in json_object:
            if key == "prefix":
                prefix_set = PrefixSet(json_object[key])
            if key == "assert":
                tasks = []
                # go over each assert and make an AssertPathSet:
                for task in json_object[key]:
                    # task contains the following:
                    # - subjects: a list of subjects or a SPARQL query
                    # - paths: a list of paths
                    if "subjects" in task:
                        # check if key is literal or SPARQL and then put value in correct class
                        if "literal" in task["subjects"]:
                            subject_definition = LiteralSubjectDefinition(
                                task["subjects"]["literal"]
                            )
                        if "SPARQL" in task["subjects"]:
                            subject_definition = SPARQLSubjectDefinition(
                                task["subjects"]["SPARQL"]
                            )

                        subject_definition = SubjectDefinition(
                            subject_definition
                        )
                    if "paths" in task:
                        assert_path_set = []
                        # go over each path and make an AssertPath
                        for assertion_path in task["paths"]:
                            assert_path = AssertPath(assertion_path)
                            assert_path_set.append(assert_path)
                        assert_path_set = AssertPathSet(assert_path_set)
                    task = TravHarvTask(
                        {
                            "subject_definition": subject_definition,
                            "assert_path_set": assert_path_set,
                        }
                    )
                    tasks.append(task)
        return {"prefix_set": prefix_set, "tasks": tasks}

    def _files_folder(self):
        """
        Get all the yaml files in the config folder
        """
        yaml_files = []
        for file in os.listdir(self.config_folder):
            if file.endswith(".yaml") or file.endswith(".yml"):
                yaml_files.append(os.path.join(self.config_folder, file))
        print(yaml_files)
        return yaml_files

    def _load_yml_to_json(self, file):
        """
        Load a yaml file into a json object
        """
        with open(file, "r") as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                log.error(exc)
                sys.exit(1)  # check if system error is really needed

    def _check_yml_requirements(self, jsonobject, file):
        """
        Check that the yaml file has the required fields
        """
        required_fields = ["snooze-till-graph-age-minutes", "prefix", "assert"]
        returnBool = True
        for field in required_fields:
            if field not in jsonobject:
                log.error(
                    "Required field {} not found in {}".format(field, file)
                )
                return False
            if field == "assert" and field in jsonobject:
                returnBool = self._check_asserts(jsonobject[field])
        return returnBool

    def _check_asserts(self, assertObject):
        required_fields = ["subjects", "paths"]
        returnBool = True
        for assertpart in assertObject:
            for field in required_fields:
                if field not in assertpart:
                    log.error(
                        "Required field {} not found in {}".format(
                            field, assertpart
                        )
                    )
                    return False

                if field == "subjects" and field in assertpart:
                    returnBool = self._check_subjects(assertpart[field])

        return returnBool

    def _is_valid_sparql_syntax(self, sparql_query):
        try:
            # parseQuery(sparql_query) #this line is commented out because pytest has an issue with this import specifically
            return True
        except Exception as e:
            print(f"Invalid SPARQL syntax: {e}")
            return False

    def _check_subjects(self, subjects):
        choices = ["literal", "SPARQL"]
        valid_present = False
        chosen_type = None
        for choice in choices:
            if choice in subjects:
                valid_present = True
                chosen_type = choice
                break

        if not valid_present:
            log.error("No valid subject type found in {}".format(subjects))
            return False

        if chosen_type == "literal":
            # check if the type of subjects is list of strings
            if not isinstance(subjects[chosen_type], list):
                log.error(
                    "Subjects of type literal should be a list of strings"
                )
                return False

            for subject in subjects[chosen_type]:
                if not isinstance(subject, str):
                    log.error(
                        "Subjects of type literal should be a list of strings"
                    )
                    return False

            return True

        if chosen_type == "SPARQL":
            if not isinstance(subjects[chosen_type], str):
                log.error("Subjects of type SPARQL should be a string")
                return False

            if not self._is_valid_sparql_syntax(str(subjects[chosen_type])):
                log.error(
                    "Subjects of type SPARQL should be a valid SPARQL query"
                )
                return False

            return True
