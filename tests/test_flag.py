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
150 @D.x@
151 @D.x.a@
152 @D.x.b@
160 @R.x@
161 @R.x.a@
162 @R.x.b@
201 ✅
202 ❌
##states##
""")

# if 'c', x is unset; goto 1
ACCEPT_C = "0 99 0 1 0"
# Let 2 be the accepting state:
ACCEPTING_STATE = "2 -1 -1 1"

POSITIVE_SET_ARCS = (
    # if a, set x <- a; goto 1
    "0 97 0 3 0",
    "3 111 1 0",
    # if 'b', set x <- b; goto 1
    "0 98 0 4 0",
    "4 112 1 0"
)

UNIFY_ARCS = (
    # if a, set x <- a; goto 1
    "0 97 0 3 0",
    "3 101 1 0",
    # if 'b', set x <- b; goto 1
    "0 98 0 4 0",
    "4 102 1 0"
)

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
    assert set(fst.generate('c')) == set()


def test_disallow_value_with_unify() -> None:
    # Given 'a', this FST will print 'b'
    # Given 'c', this FST will print both 'a', and 'b'
    fst = make_fst(
        # 1 -@D.x.a@-> 5; 5 -0:a-> (2)
        "1 151 5 0", "5 0 97 2 0",
        # 1 -@D.x.b@-> 6; 6 -0:b-> (2)
        "1 152 6 0", "6 0 98 2 0",
        a_and_b='unify'
    )

    assert set(fst.generate('a')) == {'b'}
    assert set(fst.generate('b')) == {'a'}
    assert set(fst.generate('c')) == {'a', 'b'}


def test_require_value_with_unify() -> None:
    # Given 'a', this FST will print 'b'
    # Given 'c', this FST will print both 'a', and 'b'
    fst = make_fst(
        # 1 -@R.x.a@-> 5; 5 -0:a-> (2)
        "1 161 5 0", "5 0 97 2 0",
        # 1 -@R.x.b@-> 6; 6 -0:b-> (2)
        "1 162 6 0", "6 0 98 2 0",
        a_and_b='unify'
    )

    assert set(fst.generate('a')) == {'a'}
    assert set(fst.generate('b')) == {'b'}
    assert set(fst.generate('c')) == set()


def test_unify_twice() -> None:
    # Given 'a', this FST will print 'a' (like require)
    # Given 'b', this FST will print 'b' (like require)
    # Given 'c', this FST will print both 'a', and 'b'
    #  -> it will accept the second unify without the first,
    #     unifying unconditionally.
    fst = make_fst(
        # 1 -@U.x.a@-> 5; 5 -0:a-> (2)
        "1 101 5 0", "5 0 97 2 0",
        # 1 -@U.x.b@-> 6; 6 -0:b-> (2)
        "1 102 6 0", "6 0 98 2 0",
        a_and_b='unify'
    )

    assert set(fst.generate('a')) == {'a'}
    assert set(fst.generate('b')) == {'b'}
    assert set(fst.generate('c')) == {'a', 'b'}


def test_disallow_feature() -> None:
    """
    Disallows a feature being set.
    """
    # Given 'a', this FST will reject
    # Given 'b', this FST will reject
    # Given 'c', this FST will print both 'a', and 'b'
    fst = make_fst(
        # 1 -@D.x@-> 5; 5 -0:a-> (2)
        "1 150 5 0", "5 0 97 2 0",
        # 1 -@D.x@-> 6; 6 -0:b-> (2)
        "1 150 6 0", "6 0 98 2 0",
    )

    assert set(fst.generate('a')) == set()
    assert set(fst.generate('b')) == set()
    assert set(fst.generate('c')) == {'a', 'b'}


def test_require_feature() -> None:
    """
    Requires a feature being set to any value.
    """
    # Given 'a', this FST will transduce 'a' and 'b'
    # Given 'b', this FST will transduce 'a' and 'b'
    # Given 'c', this FST will reject
    fst = make_fst(
        # 1 -@D.x@-> 5; 5 -0:a-> (2)
        "1 160 5 0", "5 0 97 2 0",
        # 1 -@D.x@-> 6; 6 -0:b-> (2)
        "1 160 6 0", "6 0 98 2 0",
    )

    assert set(fst.generate('a')) == {'a', 'b'}
    assert set(fst.generate('b')) == {'a', 'b'}
    assert set(fst.generate('c')) == set()


def make_fst(*custom_arcs: str, a_and_b='positive') -> FST:
    """
    To make a complete FST, add one or more arcs that go from state 1 to state 2.
    There are existing arcs to state 1 that set x <- a, set x <- b, and do not define x.
    """

    a_and_b_arcs = UNIFY_ARCS if a_and_b == 'unify' else POSITIVE_SET_ARCS

    arcs = (ACCEPT_C, ACCEPTING_STATE, *a_and_b_arcs, *custom_arcs)
    source = HEADER + '\n'.join(arcs) + FOOTER
    return FST.from_text(source)
