# main function here

import argparse
import os

from pytravharv.TargetStore import TargetStore
from pytravharv.TravHarvConfigBuilder import TravHarvConfigBuilder
from pytravharv.TravHarvExecuter import TravHarvExecutor

import logging
import logging.config
import yaml
import os


log = logging.getLogger("pyTravHarv")


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


class MainClass:
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
            self.travharv_config_builder.build_from_folder()
        else:
            self.travharv_config_builder.build_from_config(self.args.name)

        self.target_store = TargetStore(self.args.target_store)

        log.info(
            "Config object: {}".format(
                self.travharv_config_builder.travHarvConfig
            )
        )

        for (
            config_file,
            config,
        ) in self.travharv_config_builder.travHarvConfig.items():
            log.info("Config file: {}".format(config_file))
            log.info("Config: {}".format(config))
            self.travharvexecutor = TravHarvExecutor(
                config_file,
                config["prefix_set"],
                config["tasks"],
                self.target_store,
            )

        self.travharvexecutor.assert_all_paths()


def main():
    args = get_arg_parser().parse_args()
    main_class = MainClass(args)
    main_class.run()


if __name__ == "__main__":
    main()
