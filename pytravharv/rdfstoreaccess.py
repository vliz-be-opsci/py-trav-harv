import os
import re
import sys
import time
from typing import Optional, List
from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import (  # backup for validators since this cannot handle localhost
    quote,
    unquote,
    urlparse,
)
from rdflib import Graph
import requests
import validators
from pyrdfj2 import J2RDFSyntaxBuilder
from rdflib.plugins.sparql.processor import SPARQLResult
from SPARQLWrapper import JSON, SPARQLWrapper
from pytravharv.WebAccess import fetch
from pyrdfstore.store import RDFStore
from datetime import datetime
import logging

# log = logging.getLogger("pyTravHarv")
log = logging.getLogger(__name__)


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
    def ingest(self, graph=Graph):
        """
        Ingest given graph into teh self.graph
        """
        pass

    @abstractmethod
    def verify_max_age(self):
        """
        Get the lastmod from the registry.
        """
        pass


class RDFStoreAccess:

    def __init__(self, target: RDFStore, qryBuilder: J2RDFSyntaxBuilder):
        self._target = target
        self._qryBuilder = qryBuilder

    def select_subjects(self, sparql) -> List[str]:
        result: SPARQLResult = self._target.select(sparql)
        # todo convert response into list of subjects
        list_of_subjects = [row[0] for row in result]
        return list_of_subjects

    def verify(self, subject, property_path, prefixes=None) -> bool:
        sparql = self._qryBuilder.build_syntax(
            "trajectory.sparql",
            subject=subject,
            property_trajectory=property_path,
            prefixes=prefixes,
        )
        log.debug("subject: {}".format(subject))
        log.debug("property_path: {}".format(property_path))
        log.debug("SPARQL: {}".format(sparql))
        result: SPARQLResult = self._target.select(sparql)
        return bool(len(result.bindings) > 0)

    def ingest(self, graph: Graph, named_graph: str):
        self._target.insert(graph, named_graph)

    def verify_max_age(self, named_graph: str, age_minutes: int) -> bool:
        return self._target.verify_max_age(named_graph, age_minutes)

    def full_graph(self, named_graph: str) -> Graph:
        try:
            sparql = (
                "CONSTRUCT { ?s ?p ?o } WHERE { GRAPH <"
                + named_graph
                + "> { ?s ?p ?o } }"
            )
            return _sparqlresults_to_graph(self._target.select(sparql))
        except Exception as e:
            log.debug(e)
            sparql = "SELECT ?s ?p ?o WHERE { ?s ?p ?o } "
            return _sparqlresults_to_graph(self._target.select(sparql))


def _sparqlresults_to_graph(result: SPARQLResult) -> Graph:
    graph = Graph()
    for row in result:
        subject = row[0]
        predicate = row[1]
        _object = row[2]
        graph.add((subject, predicate, _object))

    return graph
