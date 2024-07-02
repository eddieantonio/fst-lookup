#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Controls the building of the C extension model.
"""

import os
import sysconfig
from ast import literal_eval

from setuptools import Extension  # type: ignore
from setuptools.command.build_ext import build_ext  # type: ignore

try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:
    pass
else:
    load_dotenv()


# Should we turn on debugging?
DEBUG = literal_eval(os.environ.get("FST_LOOKUP_DEBUG", "False"))
SHOULD_BUILD_EXTENSION = literal_eval(os.environ.get("FST_LOOKUP_BUILD_EXT", "True"))

# Get compiler flags from the current Python version:
extra_compile_args = (sysconfig.get_config_var("CFLAGS") or "").split()
extra_compile_args += ["-std=c99", "-Wall", "-Wextra"]

if DEBUG:
    # Enable debug symbols, assertions, and disable optimizations
    extra_compile_args += ["-g3", "-O0", "-UNDEBUG", "-Werror"]

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
    if SHOULD_BUILD_EXTENSION:
        setup_kwargs.update({"ext_modules": extensions})
