# travharv

## Description

This is a Python module that will allows an end-user to traverse given property-paths en a given config file.

## Installation

```bash
pip install travharv
```

## Usage

```python
from travharv import service
```

## dev

### overview

![overview](./py-deref-linktraversal-harvest%20UML-deref%20classes.drawio.svg)

### install dependencies

```bash
poetry install
```

### run tests

```bash
pytest
```

### how to run the code

#### example 1

This is an example of how to run the code where the targetstore is kept in memory and dumped to a file

```bash
python -m travharv -c ./tests/config/base_test.yml -d ./test.ttl -i ./tests/inputs/63523.ttl -o ./test.ttl
```

#### example 2

This is an example of how to run the code where the targetstore is a SPARQL endpoint.

```bash
python -m travharv -c ./tests/config/base_test.yml -s http://example.org http://example.org/statements
```
