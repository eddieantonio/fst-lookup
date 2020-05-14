#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Tests for the Arc class
"""

from hypothesis import given
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
