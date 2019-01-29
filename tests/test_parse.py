#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Tests for parsing the text format.
"""

import pytest  # type: ignore

from fst_lookup.parse import (Clear, Disallow, FSTParseError, Positive,
                              parse_flag, parse_text)


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


def test_parse_fst_with_flag_diacritics(english_flags_fst_txt: str) -> None:
    result = parse_text(english_flags_fst_txt)
    assert len(result.sigma) == 22
    flag_diacritics = set('@C.UN@ @D.UN@ @P.UN.ON@'.split())
    multichar_symbols = set('+Adj +Inf +Pl +V UN+ '.split())
    graphemes = set('a b d e i k l n o p r s u y'.split())
    assert len(multichar_symbols) + len(graphemes) + \
        len(flag_diacritics) == len(result.sigma)
    assert set(result.multichar_symbols.values()) == set(multichar_symbols)
    assert set(result.flag_diacritics.values()) == {
        Clear('UN'), Disallow('UN'), Positive('UN', 'ON')
    }
    assert set(result.graphemes.values()) == graphemes
    assert len(result.states) == 21
    assert len(result.arcs) == 27
    assert result.accepting_states == {20}


@pytest.mark.parametrize('raw,parsed', [
    ('@C.UN@', Clear('UN')),
    ('@D.UN@', Disallow('UN')),
    ('@P.UN.ON@', Positive('UN', 'ON')),
])
def test_parse_flag_diacritics(raw: str, parsed) -> None:
    assert parse_flag(raw) == parsed
    assert str(parsed) == raw


def test_parse_whitespace_in_sigma() -> None:
    """
    Ensures that whitespace within sigma is parsed correctly.
    """
    result = parse_text("""##foma-net 1.0##
##props##
2 390211 90019 390213 5 -1 1 2 2 1 0 2
##sigma##
0 @_EPSILON_SYMBOL_@
1 @_UNKNOWN_SYMBOL_@
2 @_IDENTITY_SYMBOL_@
3 \u0020
4 \u00A0
5 \u00AD
##states##
-1 -1 -1 -1 -1
##end##
""")
    assert len(result.sigma) == 3
    assert set(result.graphemes.values()) == {
        ' ', '\N{NO-BREAK SPACE}', '\N{SOFT HYPHEN}'
    }
