from abc import ABC, abstractmethod
from rdflib import Graph
from rdflib.plugins.sparql.processor import SPARQLResult, Result
from typing import Optional, List
from datetime import datetime, timedelta
from SPARQLWrapper import JSON, SPARQLWrapper
from pyrdfj2 import J2RDFSyntaxBuilder
import logging
from functools import reduce
from pyrdfstore import RDFStore, create_rdf_store

log = logging.getLogger(__name__)


def timestamp():
    return datetime.utcnow().isoformat()


class TargetStore(ABC):
    @abstractmethod
    def select(self, sparql: str) -> SPARQLResult:
        pass

    @abstractmethod
    def insert(self, graph: Graph, context: Optional[str] = None) -> None:
        pass

    def verify_max_age(self, context: str, age_minutes: int) -> bool:
        context_lastmod = self.lastmod_for_context(context)
        ts = datetime.utcnow()
        return bool((ts - context_lastmod).total_seconds() <= age_minutes * 60)

    @abstractmethod
    def lastmod_for_context(self, context: str) -> datetime:
        pass


class URITargetStore(TargetStore):
    """ "
    This class is used to connect to a SPARQL endpoint and execute SPARQL queries

    :param qryBuilder: helper for building sparql from templates
    :type qryBuilder: J2RDFSyntaxBuilder
    :param readURI: The URI of the SPARQL endpoint to read from
    :type readURI: str
    :param writeURI: The URI of the SPARQL endpoint to write to. If not provided, the readURI will be used.
    :type writeURI: Optional[str]
    """

    def __init__(
        self,
        qryBuilder: J2RDFSyntaxBuilder,
        read_uri: str,
        write_uri: Optional[str] = None,
    ):

        self.rdfstore = create_rdf_store(read_uri, write_uri)
        self._qryBuilder = qryBuilder

    def select(self, sparql: str) -> SPARQLResult:
        result = self.rdfstore.select(sparql)
        log.info(f"select result: {result}")
        log.info(f"type result: {type(result)}")
        return result

    def insert(self, graph: Graph, context: Optional[str] = None):
        # TODO push the graph into the store - and manage the context
        self.rdfstore.insert(graph, context)

    def lastmod_for_context(self, context: str) -> datetime:
        return self.rdfstore.lastmod_ts(context)


class MemoryTargetStore(TargetStore):
    def __init__(self):
        self._all: Graph = Graph()
        self._named_graphs = dict()
        self._admin_registry = dict()

        self.rdfstore = create_rdf_store()

    def select(self, sparql: str) -> SPARQLResult:
        return self.rdfstore.select(sparql)

    def insert(self, graph: Graph, context: Optional[str] = None):
        self.rdfstore.insert(graph, context)

    def lastmod_for_context(self, context: str) -> datetime:
        return self.rdfstore.lastmod_ts(context)


class TargetStoreAccess:

    def __init__(self, target: TargetStore, qryBuilder: J2RDFSyntaxBuilder):
        self._target = target
        self._qryBuilder = qryBuilder

    def select_subjects(self, sparql) -> List[str]:
        result: Result = self._target.select(sparql)
        # todo convert response into list of subjects
        list_of_subjects = [row[0] for row in result]
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
        list_of_bindings = [row for row in result]
        print(f"list_of_bindings: {list_of_bindings}")
        return bool(len(list_of_bindings) > 0)

    def ingest(self, graph: Graph, context: str):
        self._target.insert(graph, context)

    def full_graph(self):
        return self._target.select("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")

    def lastmod_for_context(self, context: str) -> datetime:
        return self._target.lastmod_for_context(context)
