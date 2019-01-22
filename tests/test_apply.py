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
    Parse a simple FST WITHOUT flag diacritics.
    """
    fst = FST.from_text(eat_fst_txt)
    set(fst.lookup(surface_form)) == analyses
