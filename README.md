# pyTravHarv

## Description

This is a Python module that will allows an end-user to traverse given property-paths en a given config file.

## Installation

```bash
pip install pyTravHarv
```

## Usage

```python
from pyTravHarv import pyTravHarv
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

python ./pyTravHarv/**main**.py -cf ./tests/config/ -n base_test.yml -ts ./tests/inputs/63523.ttl
