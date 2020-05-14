#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sysconfig
from distutils.command.build_ext import build_ext  # type: ignore
from distutils.core import Extension

# Get compiler flags from the current Python version:
extra_compile_args = sysconfig.get_config_vars("CFLAGS")
extra_compile_args += ["-std=c99", "-Wall", "-Wextra"]

extensions = [
    Extension(
        "fst_lookup._fst_lookup",
        sources=["fst_lookup/_fst_lookup.c"],
        extra_compile_args=extra_compile_args,
    )
]


def build(setup_kwargs):
    """
    Setup to build a C extension.
    """
    setup_kwargs.update({"ext_modules": extensions})
