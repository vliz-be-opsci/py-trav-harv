#!/usr/bin/env python
from pathlib import Path

import pytest
from conftest import TEST_CONFIG_FOLDER, TEST_INPUT_FOLDER
from util4tests import log, run_single_test

from travharv.__main__ import main


@pytest.mark.usefixtures("outpath")
def test_main(outpath: Path):
    # TODO make this run for uri_store too after conftests enables that
    # that will allow testing the -s , --store as well
    conf_path = TEST_CONFIG_FOLDER / "good_folder"
    init_path = TEST_INPUT_FOLDER / "3293.jsonld"
    dump_path = outpath / "test_main_out.ttl"
    assert not dump_path.exists(), "no output before run..."

    argsline: str = (
        f"--config {conf_path} --init {init_path} --dump {dump_path}"
    )
    log.debug(f"testing equivalent of python -mtravharv {argsline}")
    main(*argsline.split(" "))  # pass as individual arguments
    assert dump_path.exists(), "run did not create expected output"

    # TODO consider some extra assertions on the result


if __name__ == "__main__":
    run_single_test(__file__)
