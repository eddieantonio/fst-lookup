#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import gzip
from pathlib import Path

import pytest


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
    with gzip.open(str(shared_datadir / 'eat.att.gz'), 'rt') as text_file:
        return text_file.read()  # type: ignore
