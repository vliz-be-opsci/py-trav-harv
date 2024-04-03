import argparse
import logging
import logging.config
import os
from typing import Optional

import yaml

from travharv.store import TargetStore
from travharv.trav_harv_config_builder import (
    TravHarvConfig,
    TravHarvConfigBuilder,
)
from travharv.trav_harv_executer import TravHarvExecutor

# log = logging.getLogger("travharv")
log = logging.getLogger(__name__)


def get_arg_parser():
    """
    Get the argument parser for the module
    """
    parser = argparse.ArgumentParser(
        description="travharv",
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

        log.debug("type target store: {}".format(type(args.target_store)))
        log.debug(args)

        # targetstore can be a list of paths, a single path to a folder or a list of urls
        self._setup_targetstore()
        self.travharv_config_builder = TravHarvConfigBuilder(
            self.target_store, args.config_folder
        )
        self.travharvexecutor = None

    def _setup_targetstore(self):
        """checks the different arguments to see what setup will be used"""

        # arguments that can influence setup
        # -m --mode
        # -ts --target-store
        # -c --context
        # -o --output

        # if mode is memory, target store will be a temporary in-memory store memory store => it can be written to an output
        # if mode is uristore, target store will be a URI store => target store will be a list of urls and must not be empty then
        # if context is not None, it will be added to the graph when asserting paths
        # if target store is not None, it will be used as the target store

        if self.args.mode == "uristore":
            assert (
                self.args.target_store is not None
            ), "No target store provided for uristore mode. Exiting."
        self.target_store = TargetStore(
            mode=self.args.mode,
            context=self.args.context,
            store_info=self.args.target_store,
            output=self.args.output,
        )
        return

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
                raise AssertionError(
                    "No configuration found with the given name"
                )
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
