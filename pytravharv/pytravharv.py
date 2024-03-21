from typing import Optional, List
from pytravharv.common import insert_resource_into_graph
from pyrdfstore import create_rdf_store
from rdflib import Graph
from pytravharv.store import TargetStoreAccess as RDFStoreAccess
from pytravharv.common import QUERY_BUILDER
from pytravharv.TravHarvConfigBuilder import (
    TravHarvConfigBuilder,
    TravHarvConfig,
)
import yaml
import os
from pytravharv.TravHarvExecuter import TravHarvExecutor
import logging
import logging.config

# log = logging.getLogger("pyTravHarv")
log = logging.getLogger(__name__)


class TravHarv:
    """Assert all paths for given subjects.
    Given a configuration file, assert all paths for all subjects in the configuration file.
    :param config_folder: str
    :param name: str
    :param output: str
    :param context: list[str]
    :param target_store_info: Optional[list[str]]
    :param verbose: bool
    """

    def __init__(
        self,
        config_folder: str,
        name: Optional[str] = None,
        output: Optional[str] = None,
        context: Optional[List[str]] = None,
        target_store_info: Optional[List[str]] = None,
        verbose: bool = True,
    ):
        """Assert all paths for given subjects.
        Given a configuration file, assert all paths for all subjects in the configuration file.
        :param config_folder: str
        :param name: str
        :param output: str
        :param context: list[str]
        :param target_store: list[str]
        :param verbose: bool
        """
        self.config_folder = config_folder
        self.name = name
        self.output = output
        self.context = context  # have better names for this

        if verbose:
            file_location = os.path.dirname(os.path.realpath(__file__))
            with open(
                os.path.join(file_location, "debug-logconf.yml"), "r"
            ) as f:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)

            self.target_store = create_rdf_store(*target_store_info)
        self.target_store_access = RDFStoreAccess(
            self.target_store, QUERY_BUILDER
        )

        # if there is context add it to the target store
        if context is not None:
            graph = Graph()
            for context in self.context:
                insert_resource_into_graph(graph, context)
            self.target_store_access.ingest(graph, "urn:PYTRAVHARV:context")

        self.travharv_config_builder = TravHarvConfigBuilder(
            self.target_store_access, self.config_folder
        )
        self.travharvexecutor = None

    def process(self):
        try:
            log.debug("running dereference tasks")
            trav_harv_config: Optional[TravHarvConfig] = None
            if self.name is None:
                log.debug("running all configurations")
                self.travHarvConfigList = (
                    self.travharv_config_builder.build_from_folder()
                )
                log.debug(
                    "self.travHarvConfigList: {}".format(
                        self.travHarvConfigList
                    )
                )
                for trav_harv_config in self.travHarvConfigList:
                    if trav_harv_config is None:
                        continue

                    self.travharvexecutor = TravHarvExecutor(
                        trav_harv_config.configname,
                        trav_harv_config.prefixset,
                        trav_harv_config.tasks,
                        self.target_store_access,
                        self.output,
                    )
                    self.travharvexecutor.assert_all_paths()
            else:
                trav_harv_config = (
                    self.travharv_config_builder.build_from_config(self.name)
                )

                if trav_harv_config is None:
                    log.error(
                        "No configuration found with name: {}".format(
                            self.name
                        )
                    )
                    return
                self.travharvexecutor = TravHarvExecutor(
                    trav_harv_config.configname,
                    trav_harv_config.prefixset,
                    trav_harv_config.tasks,
                    self.target_store_access,
                    self.output,
                )
                self.travharvexecutor.assert_all_paths()
        except Exception as e:
            log.error(e)
            log.exception(e)
            log.error("Error running dereference tasks")
            raise e
