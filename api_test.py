from pytravharv import TravHarv
import os

config_folder = os.path.join(os.path.dirname(__file__), "tests", "config")
output_file = os.path.join(os.path.dirname(__file__), "test_output.ttl")
name = "base_test.yml"

TravHarv(
    config_folder=config_folder,
    name=name,
    output=output_file,
    context=[
        os.path.join(os.path.dirname(__file__), "tests", "inputs", "63523.ttl")
    ],
).process()

TravHarv(
    config_folder=config_folder,
    name=name,
    target_store_info=[
        "http://localhost:7200/repositories/lwua23",
        "http://localhost:7200/repositories/lwua23/statements",
    ],
).process()
