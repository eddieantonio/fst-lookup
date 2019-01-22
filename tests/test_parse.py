#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Tests for parsing the AT&T text format.
"""

import gzip

import pytest

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
    assert len(result.states) == 20
    assert len(result.arcs) == 24
    assert result.accepting_states == {19}


@pytest.fixture
def eat_fst_txt(shared_datadir) -> str:
    """
    Return the text content of the "eat" FST.

        foma[0]: read lexc eat.lexc
        1007 bytes. 20 states, 24 arcs, 6 paths.
        foma[1]: sigma
        Sigma: +3P +Mass +N +Past +PastPart +PresPart +Sg +V a e g i n s t
        Size: 15.

    """
    with gzip.open(str(shared_datadir / 'eat.att.gz'), 'rt') as text_file:
        return text_file.read()  # type: ignore
