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
    Apply up (lookup) on an FST **WITHOUT** flag diacritics.
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
