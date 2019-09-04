#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Fixtures that:

 - open the text of an FST
 - return the FST.
"""

import gzip
from pathlib import Path
from typing import cast

import pytest  # type: ignore
from fst_lookup import FST


@pytest.fixture
def eat_fst(eat_fst_txt: str) -> FST:
    """
    Return the FST that analyzes eat/eats/eaten/eating/ate.
    """
    return FST.from_text(eat_fst_txt)


@pytest.fixture
def english_flags_fst(english_flags_fst_txt: str) -> FST:
    """
    Return the FST that uses flag diacritics and tranduces
    pay/payable/unpayable/do/undo/doable/undoable.
    """
    return FST.from_text(english_flags_fst_txt)


@pytest.fixture
def english_ipa_fst(shared_datadir: Path) -> FST:
    """
    Return the FST that transcribes -ough words to IPA, including
    through/though/enough/plough/trough/tough/rough/cough/dough.
    """
    return FST.from_file(shared_datadir / "english-ipa.fomabin")


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
    with gzip.open(str(shared_datadir / "eat.fomabin"), "rt") as text_file:
        return cast(str, text_file.read())


@pytest.fixture
def english_flags_fst_txt(shared_datadir: Path) -> str:
    """
    Return the text content of the "English flags" FST.

        foma[0]: load english-flags.fomabin
        1.2 kB. 21 states, 27 arcs, 18 paths.
        foma[1]: sigma
        Sigma: +Adj +Inf +Pl +V @C.UN@ @D.UN@ @P.UN.ON@ UN+ a b d e i k l n o p r s u y
        Size: 22.
    """
    with gzip.open(str(shared_datadir / "english-flags.fomabin"), "rt") as text_file:
        return cast(str, text_file.read())
