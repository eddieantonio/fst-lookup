FST Lookup
==========

[![Build Status](https://travis-ci.org/eddieantonio/fst-lookup.svg?branch=master)](https://travis-ci.org/eddieantonio/fst-lookup)
[![codecov](https://codecov.io/gh/eddieantonio/fst-lookup/branch/master/graph/badge.svg)](https://codecov.io/gh/eddieantonio/fst-lookup)
[![PyPI version](https://img.shields.io/pypi/v/fst-lookup.svg)](https://pypi.org/project/fst-lookup/)
[![calver YYYY.MM.DD](https://img.shields.io/badge/calver-YYYY.MM.DD-22bfda.svg)](http://calver.org/)

Implements lookup for FOMA format finite state transducers.

Supports Python 3.5 and up.

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
this---note what is on each side of the colon (`:`):

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

If your FST has labels on the opposite sides, you must invert the net
before loading it into `fst_lookup`.


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

### Analyze word forms in bulk efficiently

To _analyze_ in bulk, you have the option to use `hfst-optimized-lookup`.
Call the `analyze_in_bulk()` function. For large quatities of words, it can be two orders of magnitude faster than using `fomabin` to analyze one by one:

It requires `hfst` executable installed and a `.hfstol` file. For linux system it can be an easy `sudo apt get install hfst`. For other systems check [this](https://github.com/hfst/hfst#installation).

```python
fst = FST.from_file('/MattLegend27/English_descriptive_analyzer.hfstol')
```

Note the output produced by hfstol and is different than that produced by fomabin, basically it's the concatenated version

```python
>>> fst.analyze(['eats', 'balloons', 'jjksiwks', 'does'])
[('eat+N+Mass', 'eat+V+3P+Sg'), ('balloon+N+Mass'), (''), ('do+V+3P+Sg')]
```


License
-------

Copyright © 2019 Eddie Antonio Santos. Released under the terms of the
Apache license. See `LICENSE` for more info.
