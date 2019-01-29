#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Tests for looking up in the FST.
"""

import pytest  # type: ignore

from fst_lookup import FST


@pytest.mark.parametrize('surface_form,analyses', [
    ('eat', {('eat', '+V')}),
    ('ate', {('eat', '+V', '+Past')}),
    ('eating', {('eat', '+V', '+PresPart')}),
    ('eaten', {('eat', '+V', '+PastPart')}),
    ('eats', {('eat', '+V', '+3P', '+Sg'),
              ('eat', '+N', '+Mass')}),
])
def test_analyze_eat_fst(surface_form: str, analyses: set, eat_fst_txt: str):
    """
    Apply up (analyze) on an FST **WITHOUT** flag diacritics.
    """
    fst = FST.from_text(eat_fst_txt)
    assert set(fst.analyze(surface_form)) == analyses


@pytest.mark.parametrize('analysis,surface_form', [
    (('eat' '+V'), 'eat'),
    (('eat' '+V' '+Past'), 'ate'),
    (('eat' '+V' '+PresPart'), 'eating'),
    (('eat' '+V' '+PastPart'), 'eaten'),
    (('eat' '+V' '+3P' '+Sg'), 'eats'),
    (('eat' '+N' '+Mass'), 'eats'),
])
def test_generate_eat_fst(analysis: str, surface_form: set, eat_fst_txt: str):
    """
    Apply down (generate) on an FST **WITHOUT** flag diacritics.
    """
    fst = FST.from_text(eat_fst_txt)
    actual, = fst.generate(analysis)
    assert actual == surface_form


@pytest.mark.parametrize('surface_form,analysis', [
    ('drinkables', ('drinkable', '+Adj', '+Pl')),
    ('drinkable', ('drinkable', '+Adj')),
    ('drink', ('drink', '+V', '+Inf')),
    ('payables', ('payable', '+Adj', '+Pl')),
    ('payable', ('payable', '+Adj')),
    ('pay', ('pay', '+V', '+Inf')),
    ('doables', ('doable', '+Adj', '+Pl')),
    ('doable', ('doable', '+Adj')),
    ('do', ('do', '+V', '+Inf')),
    ('undrinkables', ('UN+', 'drinkable', '+Adj' '+Pl')),
    ('undrinkable', ('UN+', 'drinkable', '+Adj')),
    ('unpayables', ('UN+', 'payable', '+Adj' '+Pl')),
    ('unpayable', ('UN+', 'payable', '+Adj')),
    ('undoables', ('UN+', 'doable', '+Adj' '+Pl')),
    ('undoable', ('UN+', 'doable', '+Adj')),
    ('undo', ('UN+', 'do', '+V' '+Inf')),
])
def test_analyze_flag_fst(surface_form: str, analysis, english_flags_fst_txt: str):
    """
    Apply up (lookup) on an FST **WITH** simple flag diacritics.
    """
    fst = FST.from_text(english_flags_fst_txt)
    assert set(fst.analyze(surface_form)) == {analysis}
