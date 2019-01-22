#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Tests for parsing the AT&T text format.
"""

from fst_lookup import parse_text


def test_parse_simple(eat_fst_txt: str):
    """
    Parse a simple FST WITHOUT flag diacritics.
    """
    result = parse_text(eat_fst_txt)
    assert len(result.sigma) == 15
    multichar_symbols = set('+3P +Mass +N +Past +PastPart '
                            '+PresPart +Sg +V'.split())
    graphemes = set('eats eaten eating ate'.replace(' ', ''))
    assert len(multichar_symbols) + len(graphemes) == len(result.sigma)
    assert set(result.multichar_symbols.values()) == set(multichar_symbols)
    assert set(result.graphemes.values()) == graphemes
    assert len(result.states) == 15
    assert len(result.arcs) == 19
    assert result.accepting_states == {14}
