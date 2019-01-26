FST Lookup
==========

[![Build Status](https://travis-ci.org/eddieantonio/fst-lookup.svg?branch=master)](https://travis-ci.org/eddieantonio/fst-lookup)
[![PyPI version](https://img.shields.io/pypi/v/fst-lookup.svg)](https://pypi.org/project/fst-lookup/)

Implements lookup for FOMA format finite state transducers.

Supports Python 3.5 and up.

Usage
-----

Import the library, and load an FST from a file:

```python
>>> from fst_lookup import FST
>>> fst = FST.from_file('eat.fst')
```

### Analysis

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


### Generate

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


License
-------

Copyright © 2019 Eddie Antonio Santos. Released under the terms of the
Apache license. See `LICENSE` for more info.
