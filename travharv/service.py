import logging
import logging.config
import os
from typing import List, Optional

import yaml
from pyrdfstore import create_rdf_store

from travharv.common import QUERY_BUILDER
from travharv.config_build import TravHarvConfig, TravHarvConfigBuilder
from travharv.executor import TravHarvExecutor
from travharv.store import TargetStoreAccess as RDFStoreAccess

# log = logging.getLogger("travharv")
log = logging.getLogger(__name__)


class TravHarv:
    """Assert all paths for given subjects.
    Given a configuration file, assert all paths
    for all subjects in the configuration file.
    :param name: str
    :param target_store_info: Optional[list[str]]
    """

    def __init__(
        self,
        config: str = None,
        target_store_info: Optional[List[str]] = None,
    ):
        """Assert all paths for given subjects.
        Given a configuration file, assert all paths
        for all subjects in the configuration file.
        :param config: str
        - The name of the configuration file.
        this can be a path to a folder containing multiple configuration files.
        or a path to a single configuration file.
        If None, all configuration files in the folder will be run.
        :param target_store: list[str]
        - The target store information. If None, a memory store will be used.
        """

        self.config = config

        file_location = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(file_location, "debug-logconf.yml"), "r") as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)

        self.target_store = create_rdf_store(*target_store_info)
        self.target_store_access = RDFStoreAccess(
            self.target_store, QUERY_BUILDER
        )

        if os.path.isdir(self.config):
            self.travharv_config_builder = TravHarvConfigBuilder(
                self.target_store_access, self.config
            )
        else:
            # take the parent of the config file as the config folder
            self.config_folder = os.path.dirname(self.config)
            self.travharv_config_builder = TravHarvConfigBuilder(
                self.target_store_access, self.config_folder
            )
        self.travharvexecutor = None

    def process(self):
        try:
            log.debug("running dereference tasks")
            trav_harv_config: Optional[TravHarvConfig] = None
            # if self.config is a path to a folder then
            # we will run all configurations in the folder
            if os.path.isdir(self.config):
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
                    )
                    self.travharvexecutor.assert_all_paths()
            else:
                trav_harv_config = (
                    self.travharv_config_builder.build_from_config(self.config)
                )

                if trav_harv_config is None:
                    log.error(
                        "No configuration found with name: {}".format(
                            self.config
                        )
                    )
                    return
                self.travharvexecutor = TravHarvExecutor(
                    trav_harv_config.configname,
                    trav_harv_config.prefixset,
                    trav_harv_config.tasks,
                    self.target_store_access,
                )
                self.travharvexecutor.assert_all_paths()
        except Exception as e:
            log.error(e)
            log.exception(e)
            log.error("Error running dereference tasks")
            raise e
