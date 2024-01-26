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
        self.target_store = target_store
        self.graph = rdflib.Graph()

    def select_subjects(self):
        # Implement method to select subjects from memory target store
        pass

    def verify(self):
        # Implement method to verify memory target store
        pass

    def ingest(self):
        # Implement method to ingest data into memory target store
        pass


class TargetStore:
    """
    A class to represent a target store to harvest from.
    The given target_store string is either a URI or a pointer to a triple store in memory.
    """

    def __init__(self, target_store=str):
        self.target_store = self._detect_type(target_store)

    def _detect_type(self):
        """
        Detect the type of the target store. if URI then use URITargetStore, filepath then use MemoryTargetStore
        """
        # Implement method to detect type of target store
        if validators.url(self.target_store):
            return URITargetStore(self.target_store)

        if os.path.isfile(self.target_store):
            return MemoryTargetStore(self.target_store)

        log.error("Target store is not a URI or a filepath")
        sys.exit(1)

    def execute(self):
        """
        Execute a SPARQL query on the target store
        """

        log.debug("Executing query on target store")
