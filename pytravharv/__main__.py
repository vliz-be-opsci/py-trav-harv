# main function here

import argparse
import os

from pytravharv.TargetStore import TargetStore
from pytravharv.TravHarvConfigBuilder import (
    TravHarvConfigBuilder,
    TravHarvConfig,
)
from pytravharv.TravHarvExecuter import TravHarvExecutor

import logging
import logging.config
import yaml
import os


# log = logging.getLogger("pyTravHarv")
log = logging.getLogger(__name__)


def get_arg_parser():
    """
    Get the argument parser for the module
    """
    parser = argparse.ArgumentParser(
        description="pyTravHarv",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print verbose output"
    )

    parser.add_argument(
        "-cf",
        "--config-folder",
        type=str,
        default=os.path.join(os.getcwd(), "config"),
        help="Folder containing configuration files, relative to the folder or file this was called from",
    )

    parser.add_argument(
        "-n",
        "--name",
        type=str,
        default=None,
        help="Name of the configuration to use",
    )

    parser.add_argument(
        "-o",
        "--output-folder",
        type=str,
        default=os.path.join(os.getcwd(), "output"),
        help="Folder to output files to",
    )

    parser.add_argument(
        "-ts",
        "--target-store",
        type=str,
        default=None,
        help="Target store to harvest, this can be a pointer to a triple store in memory or the base URI of a triple store",
    )

    return parser


class TravHarv:
    """Assert all paths for given subjects.
    Given a configuration file, assert all paths for all subjects in the configuration file.
    :param config_folder: str
    :param name: str
    :param output_folder: str
    :param target_store: str
    :param verbose: bool
    """

    def __init__(
        self,
        config_folder: str = None,
        name: str = None,
        output_folder: str = None,
        target_store: str = None,
        verbose: bool = False,
    ):
        """Assert all paths for given subjects.
        Given a configuration file, assert all paths for all subjects in the configuration file.
        :param config_folder: str
        :param name: str
        :param output_folder: str
        :param target_store: str
        :param verbose: bool
        """
        self.config_folder = config_folder
        self.name = name
        self.output_folder = output_folder
        self.target_store = target_store
        self.verbose = verbose

    def run(self):
        if self.verbose:
            file_location = os.path.dirname(os.path.realpath(__file__))
            parent_location = os.path.dirname(file_location)
            with open(
                os.path.join(parent_location, "debug-logconf.yml"), "r"
            ) as f:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)

        self.target_store = TargetStore(self.target_store)
        self.travharv_config_builder = TravHarvConfigBuilder(
            self.target_store, self.config_folder
        )
        self.travharvexecutor = None

        log.debug(self.args)

        if self.name is None:
            self.travHarvConfigList = (
                self.travharv_config_builder.build_from_folder()
            )

            for travHarvConfig in self.travHarvConfigList:
                if travHarvConfig is None:
                    continue
                log.info("Config object: {}".format(travHarvConfig()))
                # from travHarvConfig we need , prefix_set, tasks, config_file
                prefix_set = self.travHarvConfig.PrefixSet
                config_name = self.travHarvConfig.ConfigName
                tasks = self.travHarvConfig.tasks

                self.travharvexecutor = TravHarvExecutor(
                    config_name, prefix_set, tasks, self.target_store
                )

                self.travharvexecutor.assert_all_paths()
            return

        self.travHarvConfig = self.travharv_config_builder.build_from_config(
            self.name
        )
        if self.travHarvConfig is None:
            return

        log.info("Config object: {}".format(self.travHarvConfig()))

        # from travHarvConfig we need , prefix_set, tasks, config_file
        prefix_set = self.travHarvConfig.PrefixSet
        config_name = self.travHarvConfig.ConfigName
        tasks = self.travHarvConfig.tasks
        self.travharvexecutor = TravHarvExecutor(
            config_name, prefix_set, tasks, self.target_store
        )

        self.travharvexecutor.assert_all_paths()


class mainRunner:
    """
    A class to represent the main class.

    :param args: argparse.Namespace
    """

    def __init__(self, args):
        self.args = args

        if self.args.verbose:
            file_location = os.path.dirname(os.path.realpath(__file__))
            parent_location = os.path.dirname(file_location)
            with open(
                os.path.join(parent_location, "debug-logconf.yml"), "r"
            ) as f:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)

        self.target_store = TargetStore(args.target_store)
        self.travharv_config_builder = TravHarvConfigBuilder(
            self.target_store, args.config_folder
        )
        self.travharvexecutor = None

    def run(self):
        log.debug(self.args)

        if self.args.name is None:
            self.travHarvConfigList = (
                self.travharv_config_builder.build_from_folder()
            )

            for travHarvConfig in self.travHarvConfigList:
                if travHarvConfig is None:
                    continue
                log.info("Config object: {}".format(travHarvConfig()))
                # from travHarvConfig we need , prefix_set, tasks, config_file
                prefix_set = self.travHarvConfig.PrefixSet
                config_name = self.travHarvConfig.ConfigName
                tasks = self.travHarvConfig.tasks

                self.travharvexecutor = TravHarvExecutor(
                    config_name, prefix_set, tasks, self.target_store
                )

                self.travharvexecutor.assert_all_paths()

        else:
            self.travHarvConfig = (
                self.travharv_config_builder.build_from_config(self.args.name)
            )
            if self.travHarvConfig is None:
                return
            log.info("Config object: {}".format(self.travHarvConfig()))

            # from travHarvConfig we need , prefix_set, tasks, config_file
            prefix_set = self.travHarvConfig.PrefixSet
            config_name = self.travHarvConfig.ConfigName
            tasks = self.travHarvConfig.tasks

            self.travharvexecutor = TravHarvExecutor(
                config_name, prefix_set, tasks, self.target_store
            )

            self.travharvexecutor.assert_all_paths()


def main():
    args = get_arg_parser().parse_args()
    main_class = mainRunner(args)
    main_class.run()


if __name__ == "__main__":
    main()
