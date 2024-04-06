import logging
from pathlib import Path
from typing import Iterable, List
from urllib.parse import quote, unquote

from pyrdfj2 import J2RDFSyntaxBuilder
from pyrdfstore import RDFStore
from pyrdfstore.store import RDFStoreDecorator
from rdflib.plugins.sparql.processor import Result

log = logging.getLogger(__name__)


# The syntax-builder for travharv
QUERY_BUILDER: J2RDFSyntaxBuilder = J2RDFSyntaxBuilder(
    templates_folder=str(Path(__file__).parent / "templates")
)

# The default URN BASE fopr travharv
DEFAULT_URN_BASE = "urn:traversal-harvesting:"


class GraphConfigNameMapper:
    """Helper class to convert config names into graph-names."""

    def __init__(self, base: str = DEFAULT_URN_BASE) -> None:
        """constructor

        :param base: (optional) base_uri to apply,
        - defaults to DEFAULT_URN_BASE = 'urn:traversal-harvesting:'
        :type base: str
        """
        self._base = str(base)

    def cfgname_to_ng(self, cfgname: str) -> str:
        """converts local filename to a named_graph

        :param cfgname: name of the config (trav-harv job context)
        :type cfgname: str
        :returns: urn representing the filename to be used as named-graph
        :rtype: str
        """
        return f"{self._base}{quote(cfgname)}"

    def ng_to_cfgname(self, ng: str) -> str:
        """converts named_graph urn back into the local context name

        :param ng: uri of the named-graph
        :type ng: str
        :returns: the name of the matchoing travharv config context
        :rtype: str
        """
        assert ng.startswith(self._base), (
            f"Unknown {ng=}. " f"It should start with {self._base=}"
        )
        lead: int = len(self._base)
        return unquote(ng[lead:])

    def get_cfgnames_in_store(self, store: RDFStore) -> Iterable[str]:
        """selects those named graphs in the store.named_graphs under our base
        and converts them into travharv config names

        :param store: the store to grab & filter the named_graphs from
        :type store: RDFStore
        :returns: list of trvharv config names in that store
        :rtype: List[str]
        """
        return [
            self.ng_to_cfgname(ng)
            for ng in store.named_graphs
            if ng.startswith(self._base)
        ]  # filter and convert the named_graphs to config names we handle


class RDFStoreAccess(RDFStoreDecorator):
    """Decorator class adding some trav-harv specific features"""

    def __init__(self, core: RDFStore):
        super().__init__(core)
        self._qryBuilder = QUERY_BUILDER

    def select_subjects(self, sparql) -> List[str]:
        result: Result = self.select(sparql)

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

    def all_triples(self):
        return self.select("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
