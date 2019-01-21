#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from fst_lookup import FST


def test_load_from_file():
    fst = FST.from_file()
