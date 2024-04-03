import logging
from datetime import datetime
from typing import List

from pyrdfj2 import J2RDFSyntaxBuilder
from pyrdfstore import RDFStore
from rdflib import Graph
from rdflib.plugins.sparql.processor import Result

log = logging.getLogger(__name__)


class TargetStoreAccess:

    def __init__(self, target: RDFStore, qryBuilder: J2RDFSyntaxBuilder):
        self._target = target
        self._qryBuilder = qryBuilder

    def select_subjects(self, sparql) -> List[str]:
        result: Result = self._target.select(sparql)
        # if result is (400, 'HTTP Error 400: ', None) then return empty list
        if result == (400, "HTTP Error 400: ", None):
            return []

        # todo convert response into list of subjects
        list_of_subjects = [row[0] for row in result]
        log.debug(f"length list_of_subjects: {len(list_of_subjects)}")
        return list_of_subjects

    def verify_path(self, subject, property_path, prefixes=None):
        sparql = self._qryBuilder.build_syntax(
            "trajectory.sparql",
            subject=subject,
            property_trajectory=property_path,
            prefixes=prefixes,
        )
        result: Result = self._target.select(sparql)

        list_of_bindings = [row for row in result]
        return bool(len(list_of_bindings) > 0)

    def ingest(self, graph: Graph, context: str):
        self._target.insert(graph, context)

    def full_graph(self):
        return self._target.select("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")

    def lastmod_for_context(self, context: str) -> datetime:
        return self._target.lastmod_ts(context)
