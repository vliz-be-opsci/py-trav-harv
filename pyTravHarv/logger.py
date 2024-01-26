import logging
import logging.config
import yaml
import os

with open(os.path.join(os.getcwd(), "debug-logconf.yml"), "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

log = logging.getLogger(__name__)
