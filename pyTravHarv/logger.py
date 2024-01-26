import logging
import logging.config
import yaml
import os

file_location = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(file_location, "debug-logconf.yml"), "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

log = logging.getLogger(__name__)
