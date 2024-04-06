import os
from logging import getLogger
from urllib.parse import quote, unquote

from pyrdfj2 import J2RDFSyntaxBuilder

log = getLogger(__name__)

QUERY_BUILDER = J2RDFSyntaxBuilder(
    templates_folder=os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "templates"
    )
)


# TODO reconsider this common.py
# (as none of this seems/ feels common across travharv parts) --> issue #32


def graph_name_to_uri(graph_name: str) -> str:
    """
    Convert a graph name to a URI.
    """
    return "uri:PYTRAVHARV:{}".format(quote(graph_name))


def uri_to_graph_name(uri: str) -> str:
    """
    Convert a URI to a graph name.
    """
    length = len("uri:PYTRAVHARV:")
    return unquote(uri[length:])
