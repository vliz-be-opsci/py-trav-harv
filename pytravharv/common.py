from pyrdfj2 import J2RDFSyntaxBuilder
from pathlib import Path
from logging import getLogger


log = getLogger(__name__)


def make_j2rdf_builder():
    template_folder = Path(__file__).absolute().parent / "templates"
    log.info(f"template_folder == {template_folder}")
    # init J2RDFSyntaxBuilder
    j2rdf = J2RDFSyntaxBuilder(templates_folder=template_folder)
    return j2rdf


QUERY_BUILDER = make_j2rdf_builder()
