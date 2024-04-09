import logging
from html.parser import HTMLParser
from urllib.parse import urljoin

import requests
from rdflib import Graph
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

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
    subject_url: str, *, graph: Graph = None, format="turtle"
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
    :rtype: rdflib.Graph
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

    # TODO actually use the format arg to select types and load them _all_
    #      (not just the server pick as below) see --> issue #31
    headers = {"Accept": "text/turtle ,application/ld+json"}
    r = session.get(subject_url, headers=headers)

    # check if the request was successful and it returned a json-ld or ttl file
    if r.status_code == 200 and (
        "application/ld+json" in r.headers["Content-Type"]
        or "text/turtle" in r.headers["Content-Type"]
        or "application/json" in r.headers["Content-Type"]
    ):
        # parse the content directly into the triplestore
        if "text/turtle" in r.headers["Content-Type"]:
            format = "turtle"
        elif (
            "application/ld+json" in r.headers["Content-Type"]
            or "application/json" in r.headers["Content-Type"]
        ):
            format = "json-ld"

        try:
            graph.parse(data=r.text, format=format, publicID=subject_url)
            log.info(
                f"content of {subject_url} added to triplestore in {format=}"
            )
        except Exception as e:
            log.warning(
                f"failed to parse {subject_url} in {format=} error: {e}"
            )

    else:
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
            parser.close()
            return
        log.warning(
            f"request for {subject_url} failed "
            f"with status code {r.status_code} "
            f"and content type {r.headers['Content-Type']}"
        )
    return graph
