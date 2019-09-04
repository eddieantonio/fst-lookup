#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Always prefer setuptools over distutils
from setuptools import setup, find_packages  # type: ignore
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get the version from the version file!
with open(path.join(here, 'fst_lookup', '__version__.py'), encoding='UTF-8') as f:
    # Execute the __version__ file, catching its variables here:
    variables = {}  # type: ignore
    exec(f.read(), variables)
    version = variables['__version__']

setup(
    name='fst-lookup',
    version=version,
    description='Lookup Foma FSTs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/eddieantonio/fst-lookup',
    author='Eddie Antonio Santos',
    author_email='easantos@ualberta.ca',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='fst lookup transducer morphology foma',
    packages=find_packages(exclude=['docs', 'tests']),
    project_urls={
        'Bug Reports': 'https://github.com/eddieantonio/fst-lookup/issues',
        'Source': 'https://github.com/eddieantonio/fst-lookup',
    },
)
