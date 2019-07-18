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

If your FST has labels on the opposite sides--e.g., the **upper** label
corresponds to the surface form and the **upper** label corresponds to
the lemma and linguistic tags---then instantiate the FST by providing
the `labels="invert"` keyword argument:

```python
fst = FST.from_file('eat-inverted.fomabin', labels="invert")
```

If you are using `.hfstol` file, `hfst-optimized-lookup` determines the direction and you can't change it. Specify `label='hfstol'` in that case.

It requires `hfst-optimized-lookup` installed and a `.hfstol` file. For linux system it can be an easy `sudo apt get install hfst`. For other systems check [this](https://github.com/hfst/hfst#installation).


```python
fst = FST.from_file('eat.hfstol', labels="hfstol")
```

> **Hint**: FSTs originating from the HFST suite are often inverted, 
> try to loading the FST inverted first for `.generate()` and load it normally for `.analyze()`


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

### Analyze word forms in bulk

To _analyze_ in bulk, call the `analyze_in_bulk()` function. 

Note, if you use `.hfstol`, for large quatities of words, it can be orders of magnitude faster than using `fomabin`.

With the [FST for the Plains Cree language](https://github.com/UAlbertaALTLab/plains-cree-fsts), tests on a 2 core 4 threads cpu show `.hfstol` is 100 times faster when there are 500 words, 200 times faster when there are 1000 words.
```python
fst = FST.from_file('/MattLegend27/home/English_descriptive_analyzer.hfstol', labels='hfstol')
```

Note the output produced by hfstol and is different than that produced by fomabin, basically it's the concatenated version

```python
>>> fst.analyze_in_bulk(['eats', 'balloons', 'jjksiwks', 'does']) 
[('eat+N+Mass', 'eat+V+3P+Sg'), ('balloon+N+Mass'), (), ('do+V+3P+Sg')] # it's a generator of generator, expanded for simplicity here
```

### Generate word forms in bulk

Call the `generate_in_bulk()` function.

With the FST for cree language, tests on a 2 core 4 threads cpu show `.hfstol` is 100 times faster when there are 150 words, 200 times faster when there are 200 words.

```python
fst = FST.from_file('/MattLegend27/home/English_descriptive_analyzer.hfstol', labels='hfstol')
```

```python
>>> fst.generate_in_bulk(['eat+N+Mass', 'balloon+N+Mass', 'jjksiwks', 'do+V+3P+Sg'])
[('eats',), ('balloons',), (), ('does',)] # it's a generator of generator, expanded for simplicity here
```


License
-------

Copyright © 2019 Eddie Antonio Santos. Released under the terms of the
Apache license. See `LICENSE` for more info.
