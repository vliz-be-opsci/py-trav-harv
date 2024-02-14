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
from typing import Optional

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
        nargs="?",
        required=True,
        default=os.path.join(os.getcwd(), "config"),
        help="Folder containing configuration files, relative to the folder or file this was called from",
    )

    parser.add_argument(
        "-n",
        "--name",
        type=str,
        required=False,
        default=None,
        help="Name of the configuration to use",
    )

    parser.add_argument(
        "-m",
        "--mode",
        choices=["memory", "uristore"],
        default="memory",
        required=True,
        help="Mode to use, either memory or uristore. Default is memory. If memory is used, the target store will be a temporary in-memory store. If uristore is used, the target store will be a URI store.",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        required=False,
        help="File to write output to, if not specified, output will be written to stdout",
    )

    parser.add_argument(
        "-c",
        "--context",
        nargs="*",
        required=False,
        default=None,
        help="Context to add to graph when asserting paths. This will be a list of Paths to either a file containing triples or a folder containing files that can contain triples.",
    )

    parser.add_argument(
        "-ts",
        "--target-store",
        nargs=2,
        required=False,
        help="A pair of URLS for the Targetstore to harvest from. The first is the url to get statments from , the second one is to post statements to.",
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
        config_folder: str = "",
        name: str = "",
        output_folder: str = "",
        target_store: str = "",
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
            with open(
                os.path.join(file_location, "debug-logconf.yml"), "r"
            ) as f:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
        log.debug("started logging")

        self.target_store = TargetStore(self.target_store)
        self.travharv_config_builder = TravHarvConfigBuilder(
            self.target_store, self.config_folder
        )
        self.travharvexecutor = None

        log.debug("started run")

        if self.name is None:
            self.travHarvConfigList = (
                self.travharv_config_builder.build_from_folder()
            )

            for travHarvConfig in self.travHarvConfigList:
                if travHarvConfig is None:
                    continue
                log.info("Config object: {}".format(travHarvConfig()))
                # from travHarvConfig we need , prefix_set, tasks, config_file
                prefix_set = travHarvConfig.PrefixSet
                config_name = travHarvConfig.ConfigName
                tasks = travHarvConfig.tasks

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
        prefix_set = self.travHarvConfig.prefixset
        config_name = self.travHarvConfig.configname
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
            with open(
                os.path.join(file_location, "debug-logconf.yml"), "r"
            ) as f:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
        log.debug("started logging")

        self.target_store = TargetStore(args.target_store)
        self.travharv_config_builder = TravHarvConfigBuilder(
            self.target_store, args.config_folder
        )
        self.travharvexecutor = None

    def run(self):
        log.debug(self.args)
        trav_harv_config: Optional[TravHarvConfig] = None
        if self.args.name is None:
            self.travHarvConfigList = (
                self.travharv_config_builder.build_from_folder()
            )

            for trav_harv_config in self.travHarvConfigList:
                if trav_harv_config is None:
                    continue
                log.info("Config object: {}".format(trav_harv_config()))
                # from travHarvConfig we need , prefix_set, tasks, config_file
                prefix_set = trav_harv_config.prefixset
                config_name = trav_harv_config.configname
                tasks = trav_harv_config.tasks

                self.travharvexecutor = TravHarvExecutor(
                    config_name, prefix_set, tasks, self.target_store
                )

                self.travharvexecutor.assert_all_paths()

        else:
            trav_harv_config = self.travharv_config_builder.build_from_config(
                self.args.name
            )
            if trav_harv_config is None:
                return
            log.info("Config object: {}".format(trav_harv_config()))

            # from travHarvConfig we need , prefix_set, tasks, config_file
            prefix_set = trav_harv_config.prefixset
            config_name = trav_harv_config.configname
            tasks = trav_harv_config.tasks

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
