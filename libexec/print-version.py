#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
from pathlib import Path

import toml

pyproject = Path(".") / "pyproject.toml"
assert pyproject.exists()

config = toml.load(os.fspath(pyproject))
version = config["tool"]["poetry"]["version"]
print(version)
