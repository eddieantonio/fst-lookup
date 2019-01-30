#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Contrived flag diacritic tests
"""

import pytest  # type: ignore

from fst_lookup import FST

# This constructs PART of an FST
# The idea is to add arcs to this partial FST.
#
#
# Existing arcs:
#
#   consume 'a', set x <- a; goto state 1
#   consume 'b', set x <- b; goto state 1
#   consume 'c', [x is unset]; goto state 1
#
# You must add arcs that go from 1 to 2.
# The arcs in between test features of the flag diacritics.
HEADER = ("""
##foma-net 1.0##
##props##
2 17 9 1 1 1 0 1 1 0 1 2 test
##sigma##
0 @_EPSILON_SYMBOL_@
97 a
98 b
99 c
101 @U.x.a@
102 @U.x.b@
111 @P.x.a@
112 @P.x.b@
151 @D.x.a@
152 @D.x.b@
161 @R.x.a@
162 @R.x.b@
201 ✅
202 ❌
##states##
"""
          # if a, set x <- a; goto 1
          """0 97 0 3 0
3 111 1 0
"""
          # if 'b', set x <- b; goto 1
          """0 98 0 4 0
4 112 1 0
"""
          # if 'c', x is unset; goto 1
          """0 99 0 1 0
"""
          # 2 is accepting state
          """2 -1 -1 1
""")

FOOTER = """
-1 -1 -1 -1 -1
##end##
"""


def test_disallow_value() -> None:
    # Given 'a', this FST will print 'b'
    # Given 'c', this FST will print both 'a', and 'b'
    fst = make_fst(
        # 1 -@D.x.a@-> 5; 5 -0:a-> (2)
        "1 151 5 0", "5 0 97 2 0",
        # 1 -@D.x.b@-> 6; 6 -0:b-> (2)
        "1 152 6 0", "6 0 98 2 0"
    )

    assert set(fst.generate('a')) == {'b'}
    assert set(fst.generate('b')) == {'a'}
    assert set(fst.generate('c')) == {'a', 'b'}


def test_require_value() -> None:
    # Given 'a', this FST will print 'b'
    # Given 'c', this FST will print both 'a', and 'b'
    fst = make_fst(
        # 1 -@R.x.a@-> 5; 5 -0:a-> (2)
        "1 161 5 0", "5 0 97 2 0",
        # 1 -@R.x.b@-> 6; 6 -0:b-> (2)
        "1 162 6 0", "6 0 98 2 0"
    )

    assert set(fst.generate('a')) == {'a'}
    assert set(fst.generate('b')) == {'b'}
    assert set(fst.generate('c')) == {}


def make_fst(*arcs: str) -> FST:
    """
    To make a complete FST, add one or more arcs that go from state 1 to state 2.
    There are existing arcs to state 1 that set x <- a, set x <- b, and do not define x.
    """
    source = HEADER + '\n'.join(arcs) + FOOTER
    return FST.from_text(source)