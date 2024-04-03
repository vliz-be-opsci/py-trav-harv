import logging
from html.parser import HTMLParser
from urllib.parse import urljoin

import requests
from rdflib import Graph
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# log = logging.getLogger("travharv")
log = logging.getLogger(__name__)


class MyHTMLParser(HTMLParser):
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


def fetch(url):
    triplestore = Graph()
    download_uri_to_store(url, triplestore)
    return triplestore


def download_uri_to_store(uri, triplestore, format="json-ld"):
    """
    Download the uri to the triplestore

    :param uri: str
    :param triplestore: rdflib.Graph
    :param format: str
    """

    # sleep for 1 second to avoid overloading any servers => TODO make this
    # configurable and add a warning + smart retry
    total_retry = 8
    session = requests.Session()
    retry = Retry(
        total=total_retry,
        backoff_factor=0.4,  # implemented backoff formula: {backoff factor} * (2 ** ({number of total retries} - 1)) eg. 0.4 * (2 ** (8 - 1)) = 51.2 seconds on total_retry=8
        status_forcelist=[500, 502, 503, 504, 429],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    headers = {"Accept": "application/ld+json, text/turtle"}
    r = session.get(uri, headers=headers)

    # check if the request was successful and it returned a json-ld or ttl file
    if r.status_code == 200 and (
        "application/ld+json" in r.headers["Content-Type"]
        or "text/turtle" in r.headers["Content-Type"]
        or "application/json" in r.headers["Content-Type"]
    ):
        # parse the content directly into the triplestore
        if (
            "application/ld+json" in r.headers["Content-Type"]
            or "application/json" in r.headers["Content-Type"]
        ):
            format = "json-ld"
        elif "text/turtle" in r.headers["Content-Type"]:
            format = "turtle"
        try:
            triplestore.parse(data=r.text, format=format, publicID=uri)
            log.info(f"content of {uri} added to the triplestore")
        except Exception as e:
            log.warning(
                f"failed to parse {uri} with format {format} with error {e}"
            )

    else:
        # perform a check in the html to see if there is any link to fair signposting
        # perform request to uri with accept header text/html
        headers = {"Accept": "text/html"}
        r = session.get(uri, headers=headers)
        if r.status_code == 200 and "text/html" in r.headers["Content-Type"]:
            # parse the html and check if there is any link to fair signposting
            # if there is then download it to the triplestore
            log.info(f"content of {uri} is html")
            # go over the html file and find all the links in the head section
            # and check if there is any links with rel="describedby" anf if so
            # then follow it and download it to the triplestore

            parser = MyHTMLParser()
            parser.feed(r.text)
            log.info(f"found {len(parser.links)} links in the html file")
            for link in parser.links:
                # check first if the link is absolute or relative
                if link.startswith("http"):
                    absolute_url = link
                else:
                    # Resolve the relative URL to an absolute URL
                    absolute_url = urljoin(uri, link)
                # download the uri to the triplestore
                download_uri_to_store(absolute_url, triplestore)
            for script in parser.scripts:
                # parse the script and check if it is json-ld or turtle
                # if so then add it to the triplestore
                log.info(f"script: {script}")
                # { 'application/ld+json': '...'} | {'text/turtle': '...'}
                if "application/ld+json" in script:
                    log.info("found script with type application/ld+json")
                    triplestore.parse(
                        data=script["application/ld+json"],
                        format="json-ld",
                        publicID=uri,
                    )
                elif "text/turtle" in script:
                    log.info("found script with type text/turtle")
                    triplestore.parse(
                        data=script["text/turtle"],
                        format="turtle",
                        publicID=uri,
                    )
            parser.close()
            return
        log.warning(
            f"request for {uri} failed with status code {r.status_code} and content type {r.headers['Content-Type']}"
        )
