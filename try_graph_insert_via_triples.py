from rdflib import Graph


def do_try_it():
    g = Graph()
    print(f"{g=}")
    sparql = """
        INSERT DATA { GRAPH <urn:mytest> { <urn:subj> <urn:pred> <urn:obj> .} }
    """
    g.query(sparql)
    print(f"{g=}")


def main():
    do_try_it()


if __name__ == "__main__":
    main()
