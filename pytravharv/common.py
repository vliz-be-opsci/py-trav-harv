import os
from logging import getLogger
from pyrdfj2 import J2RDFSyntaxBuilder
from rdflib import Graph
from urllib.parse import quote, unquote
import validators


log = getLogger(__name__)

QUERY_BUILDER = J2RDFSyntaxBuilder(
    templates_folder=os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "templates"
    )
)


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


def insert_resource_into_graph(graph: Graph, resource: str):
    """
    Insert a resource into a graph.
    """
    # resource can be a path or a URI

    # check if resource is a URI
    if validators.url(resource):
        # get triples from the uri
        to_insert = fetch(resource)
        graph = graph + to_insert
        return graph

    # check if resource is a file
    if os.path.isfile(resource):
        # get triples from the file
        # determine the format of the file and use the correct parser
        case = resource.split(".")[-1]
        if case == "jsonld":
            graph.parse(resource, format="json-ld")
            return graph
        if case == "ttl":
            graph.parse(resource, format="ttl")
            return graph
        if case == "nt":
            graph.parse(resource, format="nt")
            return graph

    # if resource is neither a URI nor a file then raise an error
    raise ValueError(
        "Resource is not a valid URI or file path: {}".format(resource)
    )
