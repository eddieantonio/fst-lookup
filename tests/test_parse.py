#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Tests for parsing the text format.
"""

import pytest  # type: ignore

from fst_lookup.parse import parse_text, FSTParseError


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


def test_parse_multiple(eat_fst_txt: str):
    """
    Test that the parser will disallow further parses.
    """
    invalid_fst = eat_fst_txt * 2

    with pytest.raises(FSTParseError):
        parse_text(invalid_fst)


def test_parse_flag_diacritics(english_flags_fst_txt: str) -> None:
    result = parse_text(english_flags_fst_txt)
    assert len(result.sigma) == 22
    flag_diacritics = set('@C.UN@ @D.UN@ @P.UN.ON@'.split())
    multichar_symbols = set('+Adj +Inf +Pl +V UN+ '.split())
    graphemes = set('a b d e i k l n o p r s u y'.split())
    assert len(multichar_symbols) + len(graphemes) + len(flag_diacritics) == len(result.sigma)
    assert set(result.multichar_symbols.values()) == set(multichar_symbols)
    assert set(result.flag_diacritics.values()) == flag_diacritics
    assert set(result.graphemes.values()) == graphemes
    assert len(result.states) == 21
    assert len(result.arcs) == 27
    assert result.accepting_states == {20}
