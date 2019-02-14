#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import gzip
from pathlib import Path

import pytest  # type: ignore
from fst_lookup import FST


@pytest.fixture
def eat_fst_txt(shared_datadir: Path) -> str:
    """
    Return the text content of the "eat" FST.

        foma[0]: read lexc eat.lexc
        927 bytes. 15 states, 19 arcs, 6 paths.
        foma[1]: sigma
        Sigma: +3P +Mass +N +Past +PastPart +PresPart +Sg +V a e g i n s t
        Size: 15.

    """
    with gzip.open(str(shared_datadir / 'eat.fomabin'), 'rt') as text_file:
        return text_file.read()  # type: ignore


@pytest.fixture
def english_flags_fst_txt(shared_datadir: Path) -> str:
    """
    Return the text content of the "eat" FST.

        foma[0]: load english-flags.fomabin
        1.2 kB. 21 states, 27 arcs, 18 paths.
        foma[1]: sigma
        Sigma: +Adj +Inf +Pl +V @C.UN@ @D.UN@ @P.UN.ON@ UN+ a b d e i k l n o p r s u y
        Size: 22.
    """
    with gzip.open(str(shared_datadir / 'english-flags.fomabin'), 'rt') as text_file:
        return text_file.read()  # type: ignore


@pytest.fixture
def english_ipa_fst(shared_datadir: Path) -> FST:
    return FST.from_file(shared_datadir / 'english-ipa.fomabin')
