#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from fst_lookup import FST


def test_load_from_file(datadir):
    fst = FST.from_file(datadir / 'eat.att.gz')
