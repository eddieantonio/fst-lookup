#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Tests for applying (evaluating) the FST.
"""

import pytest

from fst_lookup import FST


@pytest.mark.parametrize('surface_form,analyses', [
    ('eat', {('eat', '+V')}),
    ('ate', {('eat', '+V', '+Past')}),
    ('eating', {('eat', '+V', '+PresPart')}),
    ('eaten', {('eat', '+V', '+PastPart')}),
    ('eats', {('eat', '+V', '+3P', '+Sg'),
              ('eat', '+N', '+Mass')}),
])
def test_apply_up_eat_fst(surface_form: str, analyses: set, eat_fst_txt: str):
    """
    Apply up (lookup) on an FST **WITHOUT** flag diacritics.
    """
    fst = FST.from_text(eat_fst_txt)
    assert set(fst.lookup(surface_form)) == analyses


@pytest.mark.parametrize('analysis,surface_form', [
    (('eat' '+V'), 'eat'),
    (('eat' '+V' '+Past'), 'ate'),
    (('eat' '+V' '+PresPart'), 'eating'),
    (('eat' '+V' '+PastPart'), 'eaten'),
    (('eat' '+V' '+3P' '+Sg'), 'eats'),
    (('eat' '+N' '+Mass'), 'eats'),
])
def test_lookdown_eat_fst(analysis: str, surface_form: set, eat_fst_txt: str):
    """
    Apply up (lookup) on an FST **WITHOUT** flag diacritics.
    """
    fst = FST.from_text(eat_fst_txt)
    actual, = fst.lookdown(analysis)
    assert actual == surface_form
