from logger import log

# log = logging.getLogger(__name__)
from TravHarvConfigBuilder import PrefixSet


class TravHarvExecutor:
    """
    A class to represent a TravHarvExecutor.
    This class will assert all paths for all subjects given for each task per config.
    """

    def __init__(self, config_filename: str, prefix_set: PrefixSet, tasks: list):
        self.config_filename = config_filename
        self.prefix_set = prefix_set
        self.tasks = tasks
        log.debug("TravHarvExecutor initialized")
        log.debug("Config filename: {}".format(self.config_filename))
        log.debug("Prefix set: {}".format(self.prefix_set))
        log.debug("Tasks: {}".format(self.tasks))
