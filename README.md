FST Lookup
==========

[![Build Status](https://travis-ci.org/eddieantonio/fst-lookup.svg?branch=master)](https://travis-ci.org/eddieantonio/fst-lookup)

Implements lookup for gzip'd AT&T format finite state transducers (FOMA
saves in this format).

Supports Python 3.5 and up.

Usage
-----

Import the library, and load an FST from a file:

```python
>>> from fst_lookup import FST
>>> fst = FST.from_file('eat.fst')
```

Then call `fst.lookup()` on whatever surface form you want to analyze;
`fst.lookup()` is a generator, so you must call `list()` to get back
a list.

```python
>>> list(sorted(fst.lookup('eats')))
[('eat', '+N', '+Mass'),
 ('eat', '+V', '+3P', '+Sg')]
```

License
-------

Copyright © 2019 Eddie Antonio Santos. Released under the terms of the
Apache license. See `LICENSE` for more info.
