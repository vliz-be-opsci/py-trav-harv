import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from pyrdfj2 import J2RDFSyntaxBuilder
from pyrdfstore import create_rdf_store
from rdflib import Graph
from rdflib.plugins.sparql.processor import Result, SPARQLResult
from pyrdfstore import RDFStore

log = logging.getLogger(__name__)


class TargetStoreAccess:

    def __init__(self, target: RDFStore, qryBuilder: J2RDFSyntaxBuilder):
        self._target = target
        self._qryBuilder = qryBuilder

    def select_subjects(self, sparql) -> List[str]:
        result: Result = self._target.select(sparql)
        # if result is (400, 'HTTP Error 400: ', None) then return empty list
        if result == (400, "HTTP Error 400: ", None):
            print(sparql)
            print(result)
            return []

        # todo convert response into list of subjects
        list_of_subjects = [row[0] for row in result]
        log.debug(f"length list_of_subjects: {len(list_of_subjects)}")
        return list_of_subjects

    def verify(self, subject, property_path, prefixes=None):
        sparql = self._qryBuilder.build_syntax(
            "trajectory.sparql",
            subject=subject,
            property_trajectory=property_path,
            prefixes=prefixes,
        )
        print(f"sparql: {sparql}")
        result: Result = self._target.select(sparql)
        # result is a tuple of bindings , convert into a list of bindings

        if result == (400, "HTTP Error 400: ", None):
            print(sparql)
            return False

        list_of_bindings = [row for row in result]
        print(f"len list_of_bindings: {len(list_of_bindings)}")
        return bool(len(list_of_bindings) > 0)

    def ingest(self, graph: Graph, context: str):
        self._target.insert(graph, context)

    def full_graph(self):
        return self._target.select("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")

    def lastmod_for_context(self, context: str) -> datetime:
        return self._target.lastmod_ts(context)
