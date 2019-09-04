#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Regression test for https://github.com/eddieantonio/fst-lookup/issues/4

Note:  this REQUIRES the Plains Cree analyzer:

    https://github.com/UAlbertaALTLab/plains-cree-fsts/releases/download/20190308054913-245004d/crk-descriptive-analyzer.fomabin

Place this in the tests/regressions/data/ directory.
"""

import pytest  # type: ignore
from fst_lookup import FST


def test_concatenate_lemma(shared_datadir):
    """
    Test https://github.com/eddieantonio/fst-lookup/issues/4

    Skips if the file is not found.
    """
    fst_file = shared_datadir / "crk-descriptive-analyzer.fomabin"
    if not fst_file.exists():
        pytest.skip("cannot find " + str(fst_file))

    fst = FST.from_file(fst_file)

    actual = list(fst.analyze("pimitâskosin"))
    assert [("pimitâskosin", "+V", "+AI", "+Ind", "+Prs", "+3Sg")] == actual
