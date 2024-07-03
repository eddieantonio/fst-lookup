FST Lookup
==========

[![Tests](https://github.com/eddieantonio/fst-lookup/actions/workflows/python-package.yml/badge.svg)](https://github.com/eddieantonio/fst-lookup/actions/workflows/python-package.yml)
[![codecov](https://codecov.io/gh/eddieantonio/fst-lookup/branch/master/graph/badge.svg)](https://codecov.io/gh/eddieantonio/fst-lookup)
[![PyPI version](https://img.shields.io/pypi/v/fst-lookup.svg)](https://pypi.org/project/fst-lookup/)
[![calver YYYY.MM.DD](https://img.shields.io/badge/calver-YYYY.MM.DD-22bfda.svg)](http://calver.org/)

Implements lookup for [Foma][] finite state transducers.

Supports Python 3.5 and up.

[Foma]: https://fomafst.github.io/


Install
-------

    pip install fst-lookup

Usage
-----

Import the library, and load an FST from a file:

> Hint: Test this module by [downloading the `eat` FST](https://github.com/eddieantonio/fst-lookup/raw/master/tests/data/eat.fomabin)!

```python
>>> from fst_lookup import FST
>>> fst = FST.from_file('eat.fomabin')
```

### Assumed format of the FSTs

`fst_lookup` assumes that the **lower** label corresponds to the surface
form, while the **upper** label corresponds to the lemma, and linguistic
tags and features: e.g., your `LEXC` will look something like
this—note what is on each side of the colon (`:`):

```lexc
Multichar_Symbols +N +Sg +Pl
Lexicon Root
    cow+N+Sg:cow #;
    cow+N+Pl:cows #;
    goose+N+Sg:goose #;
    goose+N+Pl:geese #;
    sheep+N+Sg:sheep #;
    sheep+N+Pl:sheep #;
```

If your FST has labels on the opposite sides—e.g., the **upper** label
corresponds to the surface form and the **upper** label corresponds to
the lemma and linguistic tags—then instantiate the FST by providing
the `labels="invert"` keyword argument:

```python
fst = FST.from_file('eat-inverted.fomabin', labels="invert")
```

> **Hint**: FSTs originating from the HFST suite are often inverted, so
> try to loading the FST inverted first if `.generate()` or `.analyze()`
> aren't working correctly!


### Analyze a word form

To _analyze_ a form (take a word form, and get its linguistic analyzes)
call the `analyze()` function:

```python
def analyze(self, surface_form: str) -> Iterator[Analysis]
```

This will yield all possible linguistic analyses produced by the FST.

An analysis is a tuple of strings. The strings are either linguistic
tags, or the _lemma_ (base form of the word).

`FST.analyze()` is a generator, so you must call `list()` to get a list.

```python
>>> list(sorted(fst.analyze('eats')))
[('eat', '+N', '+Mass'),
 ('eat', '+V', '+3P', '+Sg')]
```


### Generate a word form

To _generate_ a form (take a linguistic analysis, and get its concrete
word forms), call the `generate()` function:

```python
def generate(self, analysis: str) -> Iterator[str]
```

`FST.generate()` is a Python generator, so you must call `list()` to get
a list.

```python
>>> list(fst.generate('eat+V+Past')))
['ate']
```


Contributing
------------

If you plan to contribute code, it is recommended you use [Poetry].
Fork and clone this repository, then install development dependencies
by typing:

    poetry install

Then, do all your development within a virtual environment, managed by
Poetry:

    poetry shell

### Type-checking

This project uses `mypy` to check static types. To invoke it on this
package, type the following:

    mypy -p fst_lookup

### Running tests

To run this project's tests, we use `py.test`:

    poetry run pytest

### C Extension

Building the C extension is handled in `build.py`

To disable building the C extension, add the following line to `.env`:

```sh
export FST_LOOKUP_BUILD_EXT=False
```

(by default, this is `True`).

To enable debugging flags while working on the C extension, add the
following line to `.env`:

```sh
export FST_LOOKUP_DEBUG=TRUE
```

(by default, this is `False`).


### Fixtures

If you are creating or modifying existing test fixtures (i.e., mostly
pre-built FSTs used for testing), you will need the following
dependencies:

 * GNU `make`
 * [Foma][]

Fixtures are stored in `tests/data/`. Here, you will use `make` to
compile all pre-built FSTs from source:

    make

[Poetry]: https://github.com/python-poetry/poetry#poetry-dependency-management-for-python


License
-------

Copyright © 2019–2021 National Research Council Canada.

Licensed under the MIT license.
