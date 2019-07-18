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


@pytest.mark.parametrize('surface_form,analyses', [
    ('niskak', [('nîskâw', '+V', '+II', '+Cnj', '+Prs', '+3Sg'), ('niska', '+N', '+A', '+Pl')]),
    ('nipaw', [('nipâw', '+V', '+AI', '+Ind', '+Prs', '+3Sg')]),
    ('absolute-garbage', []),
    ('e-nipayan', [('PV/e+', 'nipâw', '+V', '+AI', '+Cnj', '+Prs', '+1Sg'),
                   ('PV/e+', 'nipâw', '+V', '+AI', '+Cnj', '+Prs', '+2Sg')]),
])
def test_cree_foma_analysis(cree_foma_analyzer: FST, surface_form, analyses):
    """
    Test that cree fomabin work
    """
    assert set(cree_foma_analyzer.analyze(surface_form)) == set(analyses)


@pytest.mark.parametrize('word,analysis', [
    (('nîskâk',), ('nîskâw', '+V', '+II', '+Cnj', '+Prs', '+3Sg')),
    (('nipâw',), ('nipâw', '+V', '+AI', '+Ind', '+Prs', '+3Sg')),
    ((), ('absolute-garbage', '+LMAO', '+Heck')),
    (('ê-nipâyân',), ('PV/e+', 'nipâw', '+V', '+AI', '+Cnj', '+Prs', '+1Sg')),
])
def test_cree_foma_generation(cree_foma_generator: FST, word, analysis):
    """
    Test that cree fomabin work
    """
    assert set(cree_foma_generator.generate(''.join(analysis))) == set(word)


@pytest.mark.parametrize('surface_forms,analyses', [
    (('nîskâk', 'nipâw', 'ê-nipâyân', 'absolute-garbage'), (
            (('nîskâw', '+V', '+II', '+Cnj', '+Prs', '+3Sg'), ('niska', '+N', '+A', '+Pl')),
            (('nipâw', '+V', '+AI', '+Ind', '+Prs', '+3Sg'),),
            (('PV/e+', 'nipâw', '+V', '+AI', '+Cnj', '+Prs', '+1Sg'),
             ('PV/e+', 'nipâw', '+V', '+AI', '+Cnj', '+Prs', '+2Sg'),),
            tuple()
    )
     )
])
def test_cree_foma_analysis_in_bulk(cree_foma_analyzer: FST, surface_forms, analyses):
    """
    Test that cree fomabin analyses in bulk
    """
    assert set(

        (map(lambda x: tuple(sorted(tuple(x))), cree_foma_analyzer.analyze_in_bulk(surface_forms)))

    ) == set(
        (map(lambda x: tuple(sorted(tuple(x))), analyses)))


@pytest.mark.parametrize('surface_forms,analyses', [
    ((('nîskâk',), ('nipâw',), ('ê-nipâyan',), tuple()), (
            (''.join(['nîskâw', '+V', '+II', '+Cnj', '+Prs', '+3Sg']),
             ''.join(['nipâw', '+V', '+AI', '+Ind', '+Prs', '+3Sg']),
             ''.join(['PV/e+', 'nipâw', '+V', '+AI', '+Cnj', '+Prs', '+2Sg']),
             ''.join(['absolute', '+Garbage', '+lmao']),)
    )
     )
])
def test_cree_foma_generation_in_bulk(cree_foma_generator: FST, surface_forms, analyses):
    """
    Test that cree fomabin generation in bulk
    """
    assert set((map(tuple, cree_foma_generator.generate_in_bulk(analyses)))) == set(surface_forms)


@pytest.mark.parametrize('surface_form,analyses', [
    ('niskak', [('nîskâw', '+V', '+II', '+Cnj', '+Prs', '+3Sg'), ('niska', '+N', '+A', '+Pl')]),
    ('nipaw', [('nipâw', '+V', '+AI', '+Ind', '+Prs', '+3Sg')]),
    ('absolute-garbage', []),
    ('e-nipayan', [('PV/e+', 'nipâw', '+V', '+AI', '+Cnj', '+Prs', '+1Sg'),
                   ('PV/e+', 'nipâw', '+V', '+AI', '+Cnj', '+Prs', '+2Sg')]),
])
def test_cree_hfstol_analysis(cree_hfstol_analyzer: FST, surface_form, analyses):
    """
    Test that cree hfstol work
    """
    assert set(cree_hfstol_analyzer.analyze(surface_form)) == set(map(lambda x: ''.join(x), analyses))


@pytest.mark.parametrize('word,analysis', [
    (('nîskâk',), ('nîskâw', '+V', '+II', '+Cnj', '+Prs', '+3Sg')),
    (('nipâw',), ('nipâw', '+V', '+AI', '+Ind', '+Prs', '+3Sg')),
    (('ê-nipâyân',), ('PV/e+', 'nipâw', '+V', '+AI', '+Cnj', '+Prs', '+1Sg')),
    (tuple(), ('absolute-garbage', '+Trash', '+Waste')),
])
def test_cree_hfstol_generation(cree_hfstol_generator: FST, word, analysis):
    """
    Test that cree hfstol work
    """
    assert set(cree_hfstol_generator.generate(''.join(analysis))) == set(word)


@pytest.mark.parametrize('surface_forms,analyses', [
    (('nîskâk', 'nipâw', 'ê-nipâyân', 'absolute-garbage'), (
            (''.join(['nîskâw', '+V', '+II', '+Cnj', '+Prs', '+3Sg']), ''.join(['niska', '+N', '+A', '+Pl'])),
            (''.join(['nipâw', '+V', '+AI', '+Ind', '+Prs', '+3Sg']),),
            (''.join(['PV/e+', 'nipâw', '+V', '+AI', '+Cnj', '+Prs', '+1Sg']),
             ''.join(['PV/e+', 'nipâw', '+V', '+AI', '+Cnj', '+Prs', '+2Sg']),),
            tuple()
    )
     )
])
def test_cree_hfstol_analysis_in_bulk(cree_hfstol_analyzer: FST, surface_forms, analyses):
    """
    Test that cree hfstol analyses in bulk
    """
    assert set((map(lambda x: tuple(sorted(tuple(x))), cree_hfstol_analyzer.analyze_in_bulk(surface_forms)))) == set(
        (map(lambda x: tuple(sorted(x)), analyses)))


@pytest.mark.parametrize('surface_forms,analyses', [
    ((('nîskâk',), ('nipâw',), ('ê-nipâyan',), tuple()), (
            (''.join(['nîskâw', '+V', '+II', '+Cnj', '+Prs', '+3Sg']),
             ''.join(['nipâw', '+V', '+AI', '+Ind', '+Prs', '+3Sg']),
             ''.join(['PV/e+', 'nipâw', '+V', '+AI', '+Cnj', '+Prs', '+2Sg']),
             ''.join(['absolute-garbage', '+Trash', '+Trash', '+Trash']),)
    )
     )
])
def test_cree_hfstol_generation_in_bulk(cree_hfstol_generator: FST, surface_forms, analyses):
    """
    Test that cree fomabin generation in bulk
    """
    assert set((map(tuple, cree_hfstol_generator.generate_in_bulk(analyses)))) == set(surface_forms)
