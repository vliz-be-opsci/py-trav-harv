import argparse
import logging
import logging.config
import os
import sys
from pathlib import Path

import validators
from rdflib import Graph

from travharv import TravHarv
from travharv.store import RDFStore, RDFStoreAccess
from travharv.web_discovery import get_description_into_graph

log = logging.getLogger(__name__)


def get_arg_parser():
    """
    Get the argument parser for the module
    """
    parser = argparse.ArgumentParser(
        description="travharv",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    DEFAULT_CONFIG_FOLDER = Path(os.getcwd()) / "config"

    parser.add_argument(
        "-c",
        "--config",
        nargs=1,
        action="store",
        type=str,
        required=False,
        default=str(DEFAULT_CONFIG_FOLDER),
        help=(
            "Path to folder containing configuration files "
            "or to a single configuration path "
            "in both cases relative to the working directory. "
            "Defaults to ./config "
        ),
    )

    parser.add_argument(
        "-d",
        "--dump",
        type=str,
        default=None,
        action="store",
        nargs=1,
        required=False,
        help=(
            "Path of file to dump the harvested resulting graph to "
            "use '-' to have output to stdout"
        ),
    )

    parser.add_argument(
        "-i",
        "--init",
        nargs="+",
        action="store",
        required=False,
        default=None,
        help=(
            "List of paths to files or folders (containing files) "
            "that will be loaded into the store at the start."
        ),
    )

    parser.add_argument(
        "-s",
        "--target-store",
        nargs=2,
        action="store",
        required=False,
        help=(
            "Pair of read_uri and write_uri describing the "
            "SPARQL endpoint to use as store. "
        ),
    )

    parser.add_argument(
        "-l",
        "--logconf",
        nargs=1,
        required=False,
        action="store",
        help=("Location of yml formatted logconfig file to apply."),
    )

    return parser


def enable_logging(args: argparse.Namespace):
    if args.logconf is None:
        return
    # conditional dependency -- we only need this (for now)
    #   when logconf needs to be read
    import yaml

    with open(args.logconf, "r") as yml_logconf:
        logging.config.dictConfig(
            yaml.load(yml_logconf, Loader=yaml.SafeLoader)
        )
    log.info(f"Logging enabled according to config in {args.logconf}")


def load_resource_into_graph(graph: Graph, resource: str):
    """
    Insert a resource into a graph.
    """
    # resource can be a path or a URI

    # check if resource is a URI
    if validators.url(resource):
        # get triples from the uri and add them
        return graph + get_description_into_graph(resource)

    # else
    resource_path: Path = Path(resource)

    # check if resource is a file
    if resource_path.is_file():
        # get triples from the file
        # determine the format of the file and use the correct parser
        ext = resource_path.suffix
        format = SUFFIX_TO_FORMAT.get(ext, "turtle")
        graph.parse(resource, format=format)
        return graph

    # else
    # check if resource is a folder
    if resource_path.is_dir():
        for sub in resource_path.glob("**/*"):
            if sub.is_dir():
                continue  # no recursion on folders, glob **/* does already
            # else
            load_resource_into_graph(graph, sub)
        return graph

    # if resource is neither a URI nor a file then raise an error
    raise ValueError(
        "Resource is not a valid URI or file path: {}".format(resource)
    )


def init_load(args: argparse.Namespace, store: RDFStore):
    """
    loads the suggested input into the store prior to execution
    """
    if args.init is None:
        log.debug("no initial context to load")
        return  # nothing to do
    # else
    log.debug(f"loading initial context from {len(args.init)=} files")
    graph: Graph = Graph()
    for inputfile in args.init:
        load_resource_into_graph(graph, inputfile)
    store.insert(graph, "urn:travharv:context")


def make_service(args) -> TravHarv:
    store_info = args.target_store or []
    config = args.config[0]
    service: TravHarv = TravHarv(config, store_info)
    return service


SUFFIX_TO_FORMAT = {
    ".ttl": "turtle",
    ".turtle": "turtle",
    ".jsonld": "json-ld",
    ".json-ld": "json-ld",
    ".json": "json-ld",
}


def final_dump(args: argparse.Namespace, store: RDFStoreAccess):
    if args.dump is None:
        log.debug("no dump expected")
        return  # nothing to do
    # else
    format = "turtle"
    outgraph = Graph()
    alltriples = store.all_triples()
    # NOTE alternatively pass Graph() as arg
    if not alltriples:
        log.debug("nothing to dump")
        return
    # else
    for triple in alltriples:
        outgraph.add(triple)

    if args.dump == "-":
        log.debug("dump to stdout")
        ser: str = outgraph.serialize(format=format)
        print(ser)
    else:
        # derive format from file extension
        log.debug(f"dump to file {args.dump}")
        dest = Path(args.dump[0])
        format = SUFFIX_TO_FORMAT.get(dest.suffix, format)
        # then save there
        outgraph.serialize(destination=dest, format=format)


def main(*cli_args):
    # parse cli args
    args: argparse.Namespace = get_arg_parser().parse_args(cli_args)
    log.debug(f"cli called with {args=}")
    # enable logging
    enable_logging(args)
    # build the core service
    service: TravHarv = make_service(args)
    # load the store initially
    init_load(args, service.target_store)
    # do what needs to be done
    service.process()
    # dump the output
    final_dump(args, service.target_store)


if __name__ == "__main__":
    # getting the cli_args here and passing them to main
    # this make the main() testable without shell subprocess
    main(sys.argv[1:])
