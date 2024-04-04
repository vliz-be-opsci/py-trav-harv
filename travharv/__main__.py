import argparse
import logging
import logging.config
import os
from pathlib import Path
from typing import Optional

import yaml
from pyrdfstore import create_rdf_store
from rdflib import Graph

from travharv.common import QUERY_BUILDER, insert_resource_into_graph
from travharv.store import TargetStoreAccess as RDFStoreAccess
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

    DEFAULT_CONFIG_FOLDER = Path(os.getcwd()) / "config"

    parser.add_argument(
        "-f",
        "--config",
        nargs="?",
        required=True,
        default=str(
            DEFAULT_CONFIG_FOLDER
        ),  # os.path.join(os.getcwd(), "config"),
        help="""Folder containing configuration files
                relative to the working directory or
                the path to a single configuration file""",
    )

    parser.add_argument(
        "-d",
        "--dump",
        type=str,
        default=None,
        required=False,
        help="""File to write output to, if not
                specified, output will be written to stdout""",
    )

    parser.add_argument(
        "-c",
        "--context",
        nargs="*",
        required=False,
        default=None,
        help="""Context to add to graph when asserting paths.
                This will be a list of Paths to either a file
                containing triples or a folder containing
                files that can contain triples.""",
    )

    parser.add_argument(
        "-s",
        "--target-store",
        nargs=2,
        required=False,
        help="""A pair of URLS for the Targetstore to harvest from.
                The first is the url to get statments from ,
                the second one is to post statements to.""",
    )

    return parser


class mainRunner:
    """
    A class to represent the main class.

    :param args: argparse.Namespace
    """

    def __init__(self, args):
        self.args = args

        file_location = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(file_location, "debug-logconf.yml"), "r") as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)

        log.debug("type target store: {}".format(type(args.target_store)))
        log.debug(args)

        self.target_store = create_rdf_store(*self.args.target_store)
        # targetstore can be a list of paths,
        # a single path to a folder or a list of urls
        self.target_store_access = RDFStoreAccess(
            self.target_store, QUERY_BUILDER
        )

        if self.args.context is not None:
            graph = Graph()
            for context in self.args.context:
                insert_resource_into_graph(graph, context)
            self.target_store_access.ingest(graph, "urn:travharv:context")

        if os.path.isdir(self.args.config):
            self.travharv_config_builder = TravHarvConfigBuilder(
                self.target_store_access, args.config
            )
        else:
            config_folder = os.path.dirname(self.args.config)
            self.travharv_config_builder = TravHarvConfigBuilder(
                self.target_store_access, config_folder
            )
        self.travharvexecutor = None

    def run(self):
        log.debug(self.args)
        trav_harv_config: Optional[TravHarvConfig] = None
        if os.path.isdir(self.args.config):
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

                graph_to_write = self.travharvexecutor.assert_all_paths()
                if self.args.dump is not None:
                    graph_to_write.serialize(self.args.dump, format="turtle")

        else:
            trav_harv_config = self.travharv_config_builder.build_from_config(
                self.args.config
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

            graph_to_write = self.travharvexecutor.assert_all_paths()
            if self.args.dump is not None:
                graph_to_write.serialize(self.args.dump, format="turtle")


def main():
    args = get_arg_parser().parse_args()
    main_class = mainRunner(args)
    main_class.run()


if __name__ == "__main__":
    main()
