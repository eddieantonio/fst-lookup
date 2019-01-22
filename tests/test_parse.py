#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Tests for parsing the AT&T text format.
"""

import gzip

from fst_lookup import parse_text


def test_parse_simple(shared_datadir):
    # foma[0]: read lexc eat.lexc
    # 1007 bytes. 20 states, 24 arcs, 6 paths.
    # foma[1]: sigma
    # Sigma: +3P +Mass +N +Past +PastPart +PresPart +Sg +V a e g i n s t
    # Size: 15.
    with gzip.open(str(shared_datadir / 'eat.att.gz'), 'rt') as text_file:
        text = text_file.read()

    result = parse_text(text)
    assert len(result.sigma) == 15
    multichar_symbols = set('+3P +Mass +N +Past +PastPart '
                            '+PresPart +Sg +V'.split())
    graphemes = set('eats eaten eating ate'.replace(' ', ''))
    assert len(multichar_symbols) + len(graphemes) == len(result.sigma)
    assert set(result.multichar_symbols.values()) == set(multichar_symbols)
    assert set(result.graphemes.values()) == graphemes
    assert len(result.states) == 20
    assert len(result.arcs) == 24
