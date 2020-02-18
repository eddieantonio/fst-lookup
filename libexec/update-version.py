#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
from pathlib import Path

import toml

pyproject = Path(".") / "pyproject.toml"
assert pyproject.exists()

config = toml.load(os.fspath(pyproject))
version = config["tool"]["poetry"]["version"]
version = config["tool"]["poetry"]["version"]

version_file = Path(".") / "fst_lookup" / "__version__.py"
CONTENTS = f"""# AUTOGENERATED FILE! DO NOT MODIFY
__version__ = {version!r}
"""
version_file.write_text(CONTENTS, encoding="UTF-8")
