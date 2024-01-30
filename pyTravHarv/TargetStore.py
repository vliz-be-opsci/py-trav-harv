import rdflib
import os
import sys

# import logging
from logger import log
import validators
from abc import ABC, abstractmethod

# log = logging.getLogger(__name__)


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


class URITargetStore(TargetStoreAccess):
    """
    A class to represent a target store to harvest from.
    The given target_store string is a URI.
    """

    def __init__(self, target_store):
        self.target_store = target_store
        self.graph = rdflib.Graph()

    def select_subjects(self):
        # Implement method to select subjects from URI target store
        pass

    def verify(self):
        # Implement method to verify URI target store
        pass

    def ingest(self):
        # Implement method to ingest data into URI target store
        pass


class MemoryTargetStore(TargetStoreAccess):
    """
    A class to represent a target store to harvest from.
    The given target_store string is a pointer to a triple store in memory.
    """

    def __init__(self, target_store):
        log.debug("MemoryTargetStore: {}".format(target_store))
        self.target_store = target_store
        self.graph = rdflib.Graph()
        self._read_file_in_graph()
        log.debug("MemoryTargetStore initialized")
        log.debug("graph: {}".format(self.graph))
        log.debug(
            "Ammount of triples in graph: {}".format(self._ammount_triples_graph())
        )

    def select_subjects(self, sparql=str):
        # Implement method to select subjects from memory target store
        return self.graph.query(sparql)

    def verify(self, sparql=str):
        # Implement method to verify for a given sparql query if there are any triples that return
        # Perform query in graph
        if len(self.graph.query(sparql)) > 0:
            return True
        return False

    def ingest(self, graph=rdflib.Graph()):
        # Implement method to ingest data into memory target store
        # combine graphs
        self.graph = self.graph + graph
        # write graph to file
        self.graph.serialize(destination=self.target_store, format="turtle")

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
        log.debug("Path to triple store file: {}".format(path_triple_store_file))

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
    """

    def __init__(self, target_store=str):
        self.target_store = self._detect_type(target_store)

    def __repr__(self) -> str:
        return "TargetStore({})".format(self.target_store)

    def get_target_store(self):
        return self.target_store

    def _detect_type(self, target_store):
        """
        Detect the type of the target store. if URI then use URITargetStore, filepath then use MemoryTargetStore
        """
        # Implement method to detect type of target store
        if validators.url(target_store):
            return URITargetStore(target_store)

        if os.path.isfile(target_store):
            return MemoryTargetStore(target_store)

        log.error("Target store is not a URI or a filepath")
        sys.exit(1)

    def execute(self):
        """
        Execute a SPARQL query on the target store
        """

        log.debug("Executing query on target store")
