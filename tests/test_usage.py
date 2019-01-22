#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from fst_lookup import FST


def test_load_from_file(shared_datadir):
    """
    Integration test for loading the FST from a file.
    """
    fst = FST.from_file(shared_datadir / 'eat.att.gz')
    # Do a transduction that outputs multiple results.
    assert set(fst.lookup('eats')) == {
            ('eat', '+N', '+Mass'),
            ('eat', '+V', '+3P', '+Sg'),
    }
