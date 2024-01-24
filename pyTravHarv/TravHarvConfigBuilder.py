import yaml
import os
import sys
import logging

log = logging.getLogger(__name__)


class TravHarvConfigBuilder:
    """
    Builds a configuration object from a given config folder
    """

    def __init__(self, configFolder):
        """
        Initialise the config builder
        """
        self.config_folder = os.path.join(
            os.path.dirname(__file__), *configFolder.split("/")
        )
        self.config_object = {}
        for file in self.files_folder():
            json_object = self.load_yml_to_json(file)
            if self.check_yml_requirements(json_object, file):
                self.config_object[file] = json_object
        log.info("Config object: {}".format(self.config_object))

    def files_folder(self):
        """
        Get all the yaml files in the config folder
        """
        yaml_files = []
        for file in os.listdir(self.config_folder):
            if file.endswith(".yaml") or file.endswith(".yml"):
                yaml_files.append(os.path.join(self.config_folder, file))
        print(yaml_files)
        return yaml_files

    def load_yml_to_json(self, file):
        """
        Load a yaml file into a json object
        """
        with open(file, "r") as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                log.error(exc)
                sys.exit(1)  # check if system error is really needed

    def check_yml_requirements(self, jsonobject, file):
        """
        Check that the yaml file has the required fields
        """
        required_fields = ["snooze-till-graph-age-minutes", "prefix", "assert"]
        returnBool = True
        for field in required_fields:
            if field not in jsonobject:
                log.error("Required field {} not found in {}".format(field, file))
                return False
            if field == "assert" and field in jsonobject:
                returnBool = self.check_asserts(jsonobject[field])
        return returnBool

    def check_asserts(self, assertObject):
        required_fields = ["subjects", "paths"]
        returnBool = True
        for assertpart in assertObject:
            for field in required_fields:
                if field not in assertpart:
                    log.error(
                        "Required field {} not found in {}".format(field, assertpart)
                    )
                    return False

                if field == "subjects" and field in assertpart:
                    returnBool = self.check_subjects(assertpart[field])

        return returnBool

    def check_subjects(self, subjects):
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
                log.error("Subjects of type literal should be a list of strings")
                return False

            for subject in subjects[chosen_type]:
                if not isinstance(subject, str):
                    log.error("Subjects of type literal should be a list of strings")
                    return False

            return True

        if chosen_type == "SPARQL":
            log.info("SPARQL not yet implemented")
            return True
