#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import pytest  # type: ignore

from fst_lookup.data import Arc, StateID
from fst_lookup.symbol import Epsilon, Grapheme


S0 = StateID(0)
S1 = StateID(1)
a = Grapheme('a')
b = Grapheme('b')


@pytest.mark.parametrize('arc,expected', [
    (Arc(S0, a, a, S1), '0 ─a→ 1'),
    (Arc(S0, a, b, S1), '0 ─a:b→ 1'),
    (Arc(S1, a, b, S0), '1 ─a:b→ 0'),
])
def test_string_arc_special(arc, expected):
    """
    Test that arcs are stringified appropriately.
    """
    assert str(arc) == expected
