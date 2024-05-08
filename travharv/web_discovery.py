import cgi
import logging
from html.parser import HTMLParser
from urllib.parse import urljoin

import requests
from rdflib import Graph
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from travharv.store import RDFStoreAccess
from travharv.execution_report import AssertionReport, TaskExecutionReport

log = logging.getLogger(__name__)


RDF_MIME_TO_FORMAT = {
    "application/ld+json": "json-ld",
    "text/turtle": "turtle",
}


def ctype_to_rdf_format(ctype: str) -> str:
    return RDF_MIME_TO_FORMAT.get(ctype, None)


class LODAwareHTMLParser(HTMLParser):
    """
    HTMLParser that knows about LOD embedding and linking techniques.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.links = []
        self.scripts = []
        self.in_script = False
        self.type = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and "rel" in attrs and attrs["rel"] == "describedby":
            if "href" in attrs:
                self.links.append(attrs["href"])
        elif (
            tag == "script"
            and "type" in attrs
            and (
                attrs["type"] == "application/ld+json"
                or attrs["type"] == "text/turtle"
            )
        ):
            self.in_script = True
            self.type = attrs["type"]

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False

    def handle_data(self, data):
        if self.in_script:
            self.scripts.append({self.type: data})


def get_description_into_graph(
    subject_url: str,
    store: RDFStoreAccess,
    config_file: str,
    assertion_report_info: dict,
    task_execution_report: TaskExecutionReport,
    format="turtle",
    graph: Graph = None,
):
    """
    Discover triples describing the subject (assumed at subject_url)
    and add them to the graph

    :param subject_url: url (originally assumed from <uri>)
    pointing to the subject to be discovered
    :type subject_url: str
    :param g: graph to be filled
    :type g: rdflib.Graph
    :param format: indicating what format should be retrieved json-ld, turtle
    :type form: str
    :returns: the graph whith added discovered triples
    :rtype: rdflib.Graph, dict
    """

    if graph is None:
        graph = Graph()  # create a fresh graph if you don't have it yet

    total_retry = 8
    session = requests.Session()
    retry = Retry(
        total=total_retry,
        backoff_factor=0.4,
        status_forcelist=[500, 502, 503, 504, 429],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    formats = ["text/turtle", "application/ld+json"]
    ACCEPTABLE_MIMETYPES = {
        "application/ld+json",
        "text/turtle",
        "application/json",
    }
    triples_found = False

    for format in formats:
        headers = {"Accept": format}
        log.debug(f"requesting {subject_url} with {headers=}")
        r = session.get(subject_url, headers=headers)
        mime_type, options = cgi.parse_header(r.headers["Content-Type"])

        if r.status_code == 200 and bool(mime_type in ACCEPTABLE_MIMETYPES):
            triples_found = True
            try:
                graph.parse(data=r.text, format=format, publicID=subject_url)
                log.info(
                    f"content of{subject_url} added to triplestore in{format=}"
                )
                assertion_report_info["assertion_result"] = True
                assertion_report_info["assertion_time"] = datetime.now()
                assertion_report_info["triple_count"] = len(graph)
                assertion_report_info["document_type"] = format
                assertion_report_info["download_url"] = subject_url
            except Exception as e:
                log.warning(
                    f"failed to parse {subject_url} in {format=} error: {e}"
                )
                assertion_report_info["assertion_result"] = False
                assertion_report_info["assertion_time"] = datetime.now()
                assertion_report_info["triple_count"] = 0
                assertion_report_info["document_type"] = format
                assertion_report_info["download_url"] = subject_url
            finally:
                # report the assertion execution report to the store
                assertion_report = AssertionReport(
                    subject_uri=subject_url,
                    assertion_path=assertion_report_info["assertion_path"],
                    assertion_result=assertion_report_info["assertion_result"],
                    assertion_time=assertion_report_info["assertion_time"],
                    id=assertion_report_info["id"],
                    download_url=assertion_report_info["download_url"],
                    rdf_store_access=store,
                    triple_count=assertion_report_info["triple_count"],
                    document_type=assertion_report_info["document_type"],
                )
                assertion_report.report_to_store()
                task_execution_report.report_to_store(assertion_report)

                # put graph into the store
                store.insert_for_config(graph, config_file)

    if not triples_found:
        # perform a check in the html to
        # see if there is any link to fair signposting
        # perform request to uri with accept header text/html
        headers = {"Accept": "text/html"}
        r = session.get(subject_url, headers=headers)
        if r.status_code == 200 and "text/html" in r.headers["Content-Type"]:
            # parse the html and check if there is any link to fair signposting
            # if there is then download it to the triplestore
            log.info(f"content of {subject_url} is html")
            # go over the html file and find all the links in the head section
            # and check if there is any links with rel="describedby" anf if so
            # then follow it and download it to the triplestore

            parser = LODAwareHTMLParser()
            parser.feed(r.text)
            log.info(f"found {len(parser.links)} links in the html file")
            for alt_url in parser.links:
                # check first if the link is absolute or relative
                if alt_url.startswith("http"):
                    alt_abs_url = alt_url
                else:
                    # Resolve the relative URL to an absolute URL
                    alt_abs_url = urljoin(subject_url, alt_url)
                # use this linked uri as the alternative for this subect
                get_description_into_graph(alt_abs_url, graph=graph)
            for script in parser.scripts:
                graph = Graph()
                # parse the script and check if it is json-ld or turtle
                # if so then add it to the triplestore
                log.info(f"script: {script}")
                # { 'application/ld+json': '...'} | {'text/turtle': '...'}
                for ctype, content in script.items():
                    cformat: str = ctype_to_rdf_format(ctype)
                    if format is None:  # ctype is not known as rdf-format
                        continue  # skip
                    log.info(f"found script with rdf {ctype=}, {cformat=}")
                    graph.parse(
                        data=content, format=cformat, publicID=subject_url
                    )

                    store.insert_for_config(graph, config_file)

                    assertion_report_info["assertion_result"] = True
                    assertion_report_info["assertion_time"] = datetime.now()
                    assertion_report_info["triple_count"] = len(graph)
                    assertion_report_info["document_type"] = cformat
                    assertion_report_info["download_url"] = subject_url

                    assertion_report = AssertionReport(
                        subject_uri=subject_url,
                        assertion_path=assertion_report_info["assertion_path"],
                        assertion_result=assertion_report_info[
                            "assertion_result"
                        ],
                        assertion_time=assertion_report_info["assertion_time"],
                        id=assertion_report_info["id"],
                        download_url=assertion_report_info["download_url"],
                        rdf_store_access=store,
                        triple_count=assertion_report_info["triple_count"],
                        document_type=assertion_report_info["document_type"],
                    )

                    assertion_report.report_to_store()
                    task_execution_report.report_to_store(assertion_report)

            parser.close()
            return
        log.warning(
            f"request for {subject_url} failed "
            f"with status code {r.status_code} "
            f"and content type {r.headers['Content-Type']}"
        )
        assertion_report_info["assertion_result"] = False
        assertion_report_info["assertion_time"] = datetime.now()
        assertion_report_info["triple_count"] = 0
        assertion_report_info["document_type"] = None
        assertion_report_info["download_url"] = subject_url

        assertion_report = AssertionReport(
            subject_uri=subject_url,
            assertion_path=assertion_report_info["assertion_path"],
            assertion_result=assertion_report_info["assertion_result"],
            assertion_time=assertion_report_info["assertion_time"],
            id=assertion_report_info["id"],
            download_url=assertion_report_info["download_url"],
            rdf_store_access=store,
            triple_count=assertion_report_info["triple_count"],
            document_type=assertion_report_info["document_type"],
        )

        assertion_report.report_to_store()
        task_execution_report.report_to_store(assertion_report)

    return
