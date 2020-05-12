#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from distutils.command.build_ext import build_ext  # type: ignore
from distutils.core import Extension

extensions = [Extension("fst_lookup._parse", sources=["fst_lookup/_parse.c"])]


def build(setup_kwargs):
    """
    Setup to build a C extension.
    """
    setup_kwargs.update({"ext_modules": extensions})
