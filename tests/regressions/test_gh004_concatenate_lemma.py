#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Regression test for https://github.com/eddieantonio/fst-lookup/issues/4

Note:  this REQUIRES the Plains Cree analyzer:

    https://github.com/UAlbertaALTLab/plains-cree-fsts/releases/download/20190308054913-245004d/crk-descriptive-analyzer.fomabin

Place this in the tests/regressions/data/ directory.
"""

from fst_lookup import FST


def test_concatenate_lemma(shared_datadir):
    fst = FST.from_file(shared_datadir / 'crk-descriptive-analyzer.fomabin')

    actual = list(fst.analyze('pimitâskosin'))
    assert [('pimitâskosin', '+V', '+AI', '+Ind', '+Prs', '+3Sg')] == actual
