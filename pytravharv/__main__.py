# main function here

import argparse
import os

from pyTravHarv.TargetStore import TargetStore
from pyTravHarv.TravHarvConfigBuilder import TravHarvConfigBuilder
from pyTravHarv.TravHarvExecuter import TravHarvExecutor

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


def main():
    """
    The main entrypoint of the module
    """
    args = get_arg_parser().parse_args()
    # check if verbose is set , if yes then enable logger
    if args.verbose:
        file_location = os.path.dirname(os.path.realpath(__file__))
        parent_location = os.path.dirname(file_location)
        with open(
            os.path.join(parent_location, "debug-logconf.yml"), "r"
        ) as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)

    log.debug(args)

    # make different classes here to use
    # TargetStore
    # TravHarvExecutor
    # TravHarvConfigBuilder
    travharv_config_builder = TravHarvConfigBuilder(args.config_folder)

    if args.name is None:
        travharv_config_builder.build_from_folder()
    else:
        travharv_config_builder.build_from_config(args.name)

    target_store = TargetStore(args.target_store)

    # some logging to see if the config is built correctly
    log.info(
        "Config object: {}".format(travharv_config_builder.travHarvConfig)
    )

    for config_file, config in travharv_config_builder.travHarvConfig.items():
        log.info("Config file: {}".format(config_file))
        log.info("Config: {}".format(config))
        travharvexecutor = TravHarvExecutor(
            config_file, config["prefix_set"], config["tasks"], target_store
        )

    travharvexecutor.assert_all_paths()


if __name__ == "__main__":
    main()
