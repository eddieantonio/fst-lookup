#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Tests for the Arc class
"""

from hypothesis import assume, given
from hypothesis.strategies import characters, integers

from fst_lookup.data import Arc, StateID
from fst_lookup.symbol import Grapheme


@given(integers(min_value=0), characters(), characters(), integers(min_value=0))
def test_eq_trivial(state, upper, lower, dest):
    s0 = StateID(state)
    s1 = StateID(dest)
    upper = Grapheme(upper)
    lower = Grapheme(lower)

    a = Arc(s0, upper, lower, s1)
    b = Arc(s0, upper, lower, s1)

    assert a == b
    assert hash(a) == hash(b)


@given(integers(min_value=0), characters(), characters(), integers(min_value=0))
def test_eq_different_symbols(state, upper, lower, dest):
    s0 = StateID(state)
    s1 = StateID(dest)

    a = Arc(s0, Grapheme(upper), Grapheme(lower), s1)
    b = Arc(s0, Grapheme(upper), Grapheme(lower), s1)

    assert a == b
    assert hash(a) == hash(b)


MAX_DISTINCT_HASH = 2 ** 16 - 1


@given(
    integers(min_value=0, max_value=MAX_DISTINCT_HASH),
    integers(min_value=1, max_value=MAX_DISTINCT_HASH),
    characters(),
    characters(),
)
def test_hash(initial: int, state_incr: int, upper: str, lower: str):
    """
    The hash function has a property that, while there are less than 2**16
    states, each arc will bucket seperately depending on its starting state.
    This helps distribute the states a bit.

    Outside of this safe range, the hash function may collide :/
    """
    s0 = StateID(initial)
    s1 = StateID(initial + state_incr)
    assert s0 < s1
    assume(s1 <= MAX_DISTINCT_HASH)

    c1 = Grapheme(upper)
    c2 = Grapheme(lower)

    a = Arc(s0, c1, c2, s0)
    b = Arc(s1, c1, c2, s0)

    assert hash(a) < hash(b)
