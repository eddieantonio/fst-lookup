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
def test_analyze_eat_fst(surface_form: str, analyses: set, eat_fst: FST):
    """
    Apply up (analyze) on an FST **WITHOUT** flag diacritics.
    """
    assert set(eat_fst.analyze(surface_form)) == analyses


@pytest.mark.parametrize('analysis,surface_form', [
    (('eat' '+V'), 'eat'),
    (('eat' '+V' '+Past'), 'ate'),
    (('eat' '+V' '+PresPart'), 'eating'),
    (('eat' '+V' '+PastPart'), 'eaten'),
    (('eat' '+V' '+3P' '+Sg'), 'eats'),
    (('eat' '+N' '+Mass'), 'eats'),
])
def test_generate_eat_fst(analysis: str, surface_form: set, eat_fst: FST):
    """
    Apply down (generate) on an FST **WITHOUT** flag diacritics.
    """
    actual, = eat_fst.generate(analysis)
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
    ('undrinkables', ('UN+', 'drinkable', '+Adj', '+Pl')),
    ('undrinkable', ('UN+', 'drinkable', '+Adj')),
    ('unpayables', ('UN+', 'payable', '+Adj', '+Pl')),
    ('unpayable', ('UN+', 'payable', '+Adj')),
    ('undoables', ('UN+', 'doable', '+Adj', '+Pl')),
    ('undoable', ('UN+', 'doable', '+Adj')),
    ('undo', ('UN+', 'do', '+V', '+Inf')),
])
def test_flag_fst(surface_form: str, analysis, english_flags_fst: FST):
    """
    Analyze and generate on an FST **WITH** simple flag diacritics.
    """
    assert set(english_flags_fst.analyze(surface_form)) == {analysis}
    assert set(english_flags_fst.generate(''.join(analysis))) == {surface_form}


@pytest.mark.parametrize('unacceptable_form', [
    'unpay', 'undrink',
])
def test_unacceptable_forms_in_flag_fst(unacceptable_form: str, english_flags_fst: FST):
    """
    Analyze forms that should not transduce on an FST **WITH** simple flag diacritics.
    """
    assert set(english_flags_fst.analyze(unacceptable_form)) == set()


def test_analyze_form_outside_of_alphabet(eat_fst: FST):
    """
    Analyzing forms with characters outside of the lower alphabet should
    reject instantly.
    """
    assert set(eat_fst.analyze('mîcisow')) == set()


def test_generate_form_outside_of_alphabet(eat_fst: FST):
    """
    Generating forms with characters outside of the upper alphabet should
    reject instantly.
    """
    assert set(eat_fst.generate('wug' '+N' '+Pl')) == set()


def test_analyze_concatenation(english_ipa_fst: FST):
    """
    Test that concatenation of the analysis works as expected when all
    elements include epsilons.
    """
    result, = english_ipa_fst.analyze('rough')
    assert result == ('ɹʌf',)
