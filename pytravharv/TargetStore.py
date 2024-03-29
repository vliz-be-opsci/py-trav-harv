import os
import re
import sys
import time
from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import (  # backup for validators since this cannot handle localhost
    quote,
    unquote,
    urlparse,
)
import rdflib
import requests
import validators
from pyrdfj2 import J2RDFSyntaxBuilder
from rdflib.plugins.sparql.processor import SPARQLResult
from SPARQLWrapper import JSON, SPARQLWrapper
from datetime import datetime
import logging

# log = logging.getLogger("pyTravHarv")
log = logging.getLogger(__name__)


def get_j2rdf_builder():
    template_folder = os.path.join(
        os.path.dirname(__file__), "pysubyt_templates"
    )
    log.info(f"template_folder == {template_folder}")
    # init J2RDFSyntaxBuilder
    j2rdf = J2RDFSyntaxBuilder(templates_folder=template_folder)
    return j2rdf


J2RDF = get_j2rdf_builder()


class TargetStoreAccess(ABC):
    """
    Abstract base class for accessing a target store.
    """

    @abstractmethod
    def select_subjects(self, sparsl=str):
        """
        Select subjects from the target store using a SPARQL query.
        """
        pass

    @abstractmethod
    def verify(self, subject=str, property_path=str):
        """
        Verify a given subject using a property path to see if this returns triples.
        """
        pass

    @abstractmethod
    def ingest(self, graph=rdflib.Graph()):
        """
        Ingest given graph into teh self.graph
        """
        pass

    @abstractmethod
    def lastmod(self):
        """
        Get the lastmod from the registry.
        """
        pass


class URITargetStore(TargetStoreAccess):
    """
    A class to represent a target store to harvest from.
    The given target_store string is a URI.

    :param target_store: The target store to harvest from.
    :type target_store: str
    """

    def __init__(self, target_store):
        self.target_store = target_store
        self.graph = rdflib.Graph()
        self.GDB = self._detect_type_remote_store()

    def select_subjects(self, sparql=str):
        """Select subjects from the target store using a SPARQL query.

        :param sparql: The SPARQL query to use.
        :type sparql: str

        :return: The result of the SPARQL query.
        :rtype: SPARQLResult
        """
        # Implement method to select subjects from URI target store
        # query the remote store self.GBD
        # log.debug("GDB: {}".format(self.GDB))
        # must return a SPARQLresult object
        self.GDB.setQuery(sparql)
        self.GDB.setReturnFormat(JSON)
        result = self.GDB.query().convert()
        log.debug("results_dict: {}".format(result))

        # given that a SPARQLResult object is expected, convert the result to a SPARQLResult object
        result_mapped = {
            "type_": "SELECT",
            "vars_": result["head"]["vars"],
            "bindings": result["results"]["bindings"],
            "askAnswer": None,  # Assuming the askAnswer is not available in the result
            "graph": None,  # Assuming the graph is not available in the result
        }

        result = SPARQLResult(result_mapped)
        return result

    def verify(self, query=str):
        """
        Verify a given subject using a property path to see if this returns triples.

        :param query: The query to use.
        :type query: str

        :return: True if the query returns triples, False otherwise.
        :rtype: bool
        """

        # Implement method to verify URI target store
        # query the remote store self.GBD
        # log.debug("GDB: {}".format(self.GDB))
        self.GDB.setQuery(query)
        results = self.GDB.query().convert()
        # TODO: excercise when the results come from a non GRAPHDB endpoint
        # TODO: check whether the results have the same return format as the select_subjects method
        log.debug("results GDB verify: {}".format(results))
        if len(results["results"]["bindings"]) > 0:
            return True
        return False

    def ingest(self, graph=rdflib.Graph(), context: str = None):
        """
        Ingest given graph into the remote store.

        :param graph: The graph to ingest.
        :type graph: Graph
        :param context: The context to ingest the graph into.
        :type context: str
        """

        # Implement method to ingest data into URI target store
        # ingest the graph into the remote store self.GBD
        log.debug("ingest graph: {}".format(graph))
        log.debug("context: {}".format(context))
        # for now only GRAPHDB is supported
        # context is reduced to none
        context = self._context_2_urn(context)
        self._batch_insert_graph(graph, context)

    def lastmod(self):
        """
        Get the lastmod from the registry.
        """
        # Implement method to get the lastmod from the registry
        return self._get_registry_lastmod()

    def _context_2_urn(self, context: str):
        """
        Convert a context to a URN.
        """
        # Implement method to convert a context to a URN
        # convert the context into a str that is uri compliant
        safe_context = quote(context)
        return f"urn:PYTRAVHARV:{safe_context}"

    def _urn_2_context(self, urn: str):
        """
        Convert a context to a filename path.

        :param context: The context to convert.
        :type context: str
        :return: The filename corresponding to the context.
        :rtype: str
        """
        return unquote(urn[len("urn:PYTRAVHARV:") :])

    def _batch_insert_graph(
        self, graph: rdflib.Graph(), context: str = None, batch_size: int = 100
    ):
        """
        Insert data into a context in batches.

        :param graph: The graph to insert data from.
        :type graph: Graph
        :param context: The context to insert data into.
        :type context: str
        :param batch_size: The batch size to use.
        :type batch_size: int
        """

        # Variables for the template
        template = "insert_graph.sparql"
        ntstr = graph.serialize(format="nt")

        # log the size fo the ntstr
        log.info(f"ntstr size: {len(ntstr)}")

        # Split ntstr by newline to get a list of triples
        non_unique_triples = ntstr.split("\n")

        triples = list(set(non_unique_triples))

        # Initialize an empty list to hold the batches
        ntstr_batches = []

        # Loop over the list of triples with a step size of batch_size
        for i in range(0, len(triples), batch_size):
            # Slice the list of triples from the current index to the current index plus batch_size
            # Join them with newline to get a batch
            batch = "\n".join(triples[i : i + batch_size])

            # Append the batch to ntstr_batches
            ntstr_batches.append(batch)

        log.info(
            f"insert_graph into {context} in {len(ntstr_batches)} batches"
        )

        for batch in ntstr_batches:
            # Variables for the template
            vars = {"context": context, "raw_triples": batch}
            query = J2RDF.build_syntax(template, **vars)

            self.GDB.setQuery(query)
            self.GDB.query()

            # update the admin graph
            # get current time in utc
            lastmod = datetime.utcnow().isoformat()
            self._update_registry_lastmod(lastmod, context)

    def _detect_type_remote_store(self):
        """TODO: Implement method to detect type of remote target store.
        For now there is only an endpoint for GRAPHDB repositories.
        """
        GRAPHDB_RE = r"http://([\w.-]+:\d+)/repositories/(\w+)"
        match = re.match(GRAPHDB_RE, self.target_store)
        if match:
            return self._graphDB_config()

        # TODO: add more remote target store types

        # if no match is found then try and get a request to get all possible graph of a store
        # if this fails then raise an error that the store given is not a valid remote store
        if self._detect_repos_for_graphdb() is not None:
            # return a table like overview of what repositories are avialable
            log.debug(
                "repositories: {}".format(self._detect_repos_for_graphdb())
            )
            raise ValueError(
                "Target store is not a valid remote store URI, use one of the following repositories: {}".format(
                    self._detect_repos_for_graphdb()
                )
            )

        raise ValueError(
            "Target store is not a valid remote store URI: {}".format(
                self.target_store
            )
        )

    def _detect_repos_for_graphdb(self):
        """
        Detect the repositories for a GRAPHDB endpoint.
        """
        # Implement method to detect the repositories for a GRAPHDB endpoint do accept application/json
        response = requests.get(
            f"{self.target_store}/repositories",
            headers={"Accept": "application/json"},
        )
        if response.status_code == 200:
            response_json = response.json()
            # Extract 'uri' and 'id' from the response
            uri_and_id = [
                {"uri": repo["uri"]["value"], "id": repo["id"]["value"]}
                for repo in response_json["results"]["bindings"]
            ]
            log.debug("uri and id: {}".format(uri_and_id))
            return uri_and_id
        return None

    def _graphDB_config(self):
        """
        Setup graphdb config
        """
        # Implement method to get the graphDB config
        self.endpoint = self.target_store
        self.updateEndpoint = self.target_store + "/statements"

        GDB = SPARQLWrapper(
            endpoint=self.endpoint,
            updateEndpoint=self.updateEndpoint,
            returnFormat=JSON,
            agent="lwua-python-sparql-client",
        )
        GDB.method = "POST"
        return GDB

    def _update_registry_lastmod(self, lastmod: str, context: str = None):
        """
        Update the registry lastmod.
        """
        # Implement method to update the registry lastmod
        # update the lastmod in the registry
        # the lastmod is a string that is a datetime
        # use the lastmod to update the registry
        # the registry is a graph in the target store
        # the lastmod is a property of the graph
        # the lastmod is a datetime string
        # the lastmod is updated with the current datetime
        template = "update_registry_lastmod.sparql"
        admin_context = "ADMIN"
        vars = {
            "context": context if context is not None else None,
            "lastmod": lastmod if lastmod is not None else None,
            "registry_of_lastmod_context": self._context_2_urn(admin_context),
        }
        query = J2RDF.build_syntax(template, **vars)
        log.debug("query: {}".format(query))
        self.GDB.setQuery(query)
        self.GDB.query()

    def _get_registry_lastmod(self, context: str = None):
        """
        Get the lastmod from the registry.
        """
        # Implement method to get the lastmod from the registry
        # get the lastmod from the registry
        # the lastmod is a property of the graph
        # the lastmod is a datetime string
        # the lastmod is updated with the current datetime
        template = "lastmod_info.sparql"
        admin_context = "ADMIN"
        vars = {
            "registry_of_lastmod_context": self._context_2_urn(admin_context),
        }
        query = J2RDF.build_syntax(template, **vars)
        log.debug("query: {}".format(query))
        self.GDB.setQuery(query)
        self.GDB.setReturnFormat(JSON)
        result = self.GDB.query().convert()
        log.debug("result: {}".format(result))
        return self._convert_results_registry_of_lastmod(result)

    def _convert_results_registry_of_lastmod(self, results):
        converted = {}
        for g in results["results"]["bindings"]:
            path = self._urn_2_context(g["graph"]["value"])
            time = datetime.strptime(
                g["lastmod"]["value"], "%Y-%m-%dT%H:%M:%S.%f"
            )
            converted[path] = time
        return converted


class MemoryTargetStore(TargetStoreAccess):
    """
    A class to represent a target store to harvest from.
    The given target_store string is a pointer to a triple store in memory.

    :param target_store: The target store to harvest from.
    :type target_store: str
    """

    def __init__(self, target_store):
        log.debug("MemoryTargetStore: {}".format(target_store))
        self.target_store = target_store
        self.graph = rdflib.Graph()
        self._read_file_in_graph()
        log.debug("MemoryTargetStore initialized")
        log.debug("graph: {}".format(self.graph))
        log.debug(
            "Ammount of triples in graph: {}".format(
                self._ammount_triples_graph()
            )
        )

    def select_subjects(self, sparql=str):
        """Select subjects from the target store using a SPARQL query.

        :param sparql: The SPARQL query to use.
        :type sparql: str

        :return: The result of the SPARQL query.
        :rtype: SPARQLResult
        """
        # Implement method to select subjects from memory target store
        results = self.graph.query(sparql)
        log.debug("results: {}".format(results))
        # explode the results to get the indiv subjects
        results_dict = []
        for result in results:
            results_dict.append(result)
        log.debug("results_dict: {}".format(results_dict))
        return results

    def verify(self, sparql=str):
        """
        Verify a given subject using a property path to see if this returns triples.

        :param query: The query to use.
        :type query: str

        :return: True if the query returns triples, False otherwise.
        :rtype: bool
        """
        # Implement method to verify for a given sparql query if there are any triples that return
        # Perform query in graph
        if len(self.graph.query(sparql)) > 0:
            return True
        return False

    def ingest(self, graph=rdflib.Graph(), context: str = None):
        """
        Ingest given graph into the remote store.

        :param graph: The graph to ingest.
        :type graph: Graph
        :param context: The context to ingest the graph into.
        :type context: str
        """
        # get all unique triples before adding them to the graph
        u_list_triples = list(graph)

        new_graph = rdflib.Graph()
        for triples in u_list_triples:
            new_graph.add(triples)
        graph = new_graph
        # combine graphs
        self.graph = self.graph + graph
        # write graph to file
        self.graph.serialize(destination=self.target_store, format="turtle")

    def lastmod(self):
        return None

    def _ammount_triples_graph(self):
        """
        Get the ammount of triples in the graph
        """
        return len(self.graph)

    def _read_file_in_graph(self):
        """
        Read in the target store
        """
        # read in the target_store into self.graph this can be a ttl of a jsonld file
        # if file ends in .jsonld then use jsonld
        # if file ends in .ttl then use turtle
        # if file ends in .nt then use nt
        if self.target_store.endswith(".jsonld"):
            self.graph.parse(self.target_store, format="json-ld")
            return
        if self.target_store.endswith(".ttl"):
            self.graph.parse(self.target_store, format="turtle")
            return
        if self.target_store.endswith(".nt"):
            self.graph.parse(self.target_store, format="nt")
            return
        log.error(
            "Target store is not a valid file extension. Please use .jsonld, .ttl or .nt"
        )

    def _create_graph(self):
        """
        Create a graph from the given target store
        """
        # Target store is from a given os path
        path_triple_store_file = os.path.join(os.getcwd(), self.target_store)
        log.debug(
            "Path to triple store file: {}".format(path_triple_store_file)
        )

        # Check if the file exists
        if not os.path.isfile(path_triple_store_file):
            log.error("Triple store file does not exist")
            sys.exit(1)

        # Depending on the file extension, use the correct parser
        # supported formats for parsing are , jsonLD , ttl
        log.debug("Parsing triple store file")
        if self.target_store.endswith(".jsonld"):
            self.graph.parse(path_triple_store_file, format="json-ld")
        elif self.target_store.endswith(".ttl"):
            self.graph.parse(path_triple_store_file, format="ttl")
        else:
            log.error("Triple store file format not supported")
            sys.exit(1)


class TargetStore:
    """
    A class to represent a target store to harvest from.
    The given target_store string is either a URI or a pointer to a triple store in memory.

    :param target_store: The target store to harvest from.
    :type target_store: str
    :raises ValueError: If the target store is not a URI or a filepath.
    :raises SystemExit: If the target store is not a URI or a filepath.
    :return: The target store to harvest from.
    :rtype: TargetStore
    """

    def __init__(self, target_store=str):
        self.target_store = self._detect_type(target_store)

    def __repr__(self) -> str:
        return "TargetStore({})".format(self.target_store)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.target_store

    def get_target_store(self):
        return self.target_store

    def _detect_type(self, target_store):
        """
        Detect the type of the target store. if URI then use URITargetStore, filepath then use MemoryTargetStore
        """

        if os.path.isfile(target_store):
            return MemoryTargetStore(target_store)

        # Implement method to detect type of target store
        if _is_valid_url(target_store):
            return URITargetStore(target_store)

        log.debug("TargetStore: {}".format(target_store))
        log.error("Target store is not a URI or a filepath")
        sys.exit(1)


def _is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        if validators.url(url):
            return True
        return False
