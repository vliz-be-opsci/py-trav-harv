from typing import Optional, List
from pytravharv.TargetStore import TargetStore
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
    :param target_store: list[str]
    :param verbose: bool
    """

    def __init__(
        self,
        config_folder: str,
        mode: str,
        name: Optional[str],
        output: Optional[str],
        context: Optional[List[str]],
        target_store: Optional[List[str]],
        verbose: bool = False,
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
        self.mode = mode
        self.output = output
        self.context = context
        self.target_store = target_store
        self.verbose = verbose

        if self.verbose:
            file_location = os.path.dirname(os.path.realpath(__file__))
            with open(
                os.path.join(file_location, "debug-logconf.yml"), "r"
            ) as f:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
        log.debug("started logging")

        self._setup_targetstore()
        self.travharv_config_builder = TravHarvConfigBuilder(
            self.target_store, self.config_folder
        )
        self.travharvexecutor = None

    def run_dereference_tasks(self):
        log.debug("running dereference tasks")
        trav_harv_config: Optional[TravHarvConfig] = None
        if self.name is None:
            self.travHarvConfigList = (
                self.travharv_config_builder.build_from_folder()
            )

            for trav_harv_config in self.travHarvConfigList:
                if trav_harv_config is None:
                    continue

                self.travharvexecutor = TravHarvExecutor(
                    trav_harv_config.configname,
                    trav_harv_config.prefixset,
                    trav_harv_config.tasks,
                    self.target_store,
                )
                self.travharvexecutor.assert_all_paths()
        else:
            trav_harv_config = self.travharv_config_builder.build_from_config(
                self.name
            )

            if trav_harv_config is None:
                log.error(
                    "No configuration found with name: {}".format(self.name)
                )
                return
            self.travharvexecutor = TravHarvExecutor(
                trav_harv_config.configname,
                trav_harv_config.prefixset,
                trav_harv_config.tasks,
                self.target_store,
            )
            self.travharvexecutor.assert_all_paths()

    def _setup_targetstore(self):
        """checks the different arguments to see what setup will be used"""

        if self.mode == "uristore":
            assert (
                self.target_store is not None
            ), "No target store provided for uristore mode. Exiting."
        self.target_store = TargetStore(
            mode=self.mode,
            context=self.context,
            store_info=self.target_store,
            output=self.output,
        )
        return
