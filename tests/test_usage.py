#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import pytest  # type: ignore

from fst_lookup import FST


def test_load_from_file(shared_datadir):
    """
    Integration test for loading the FST from a file.
    """
    fst = FST.from_file(shared_datadir / "eat.fomabin")
    # Do a transduction that outputs multiple results.
    assert set(fst.analyze("eats")) == {
        ("eat", "+N", "+Mass"),
        ("eat", "+V", "+3P", "+Sg"),
    }
    # Transduce the other way!
    assert set(fst.generate("eat" "+V" "+Past")) == {"ate"}


def test_load_from_file_flipped(shared_datadir):
    """
    Integration test loading an FST from a file where its
    UPPER side is the surface form, and its
    LOWER side is the deep form
    (following HFST conventions rather and XFST conventions).
    """
    fst = FST.from_file(shared_datadir / "tae.fomabin", labels="invert")

    # The following tests are INTENTIONALLY the same as for
    # test_load_from_file(). However, the FST is different than in that test.

    # Do a transduction that outputs multiple results.
    assert set(fst.analyze("eats")) == {
        ("eat", "+N", "+Mass"),
        ("eat", "+V", "+3P", "+Sg"),
    }
    # Transduce the other way!
    assert set(fst.generate("eat" "+V" "+Past")) == {"ate"}


@pytest.mark.parametrize("labels", [False, True, "inverse", "standard", "", None])
def test_invalid_invocation(labels, shared_datadir):
    """
    Try using an incorrect parameters for labels
    """

    with pytest.raises(ValueError):
        FST.from_file(shared_datadir / "eat.fomabin", labels=labels)
