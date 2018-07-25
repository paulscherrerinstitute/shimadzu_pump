#!/usr/bin/env python
from setuptools import setup

exec(open("version.py").read())

setup(
    name=__name__,
    version=__version__,
    description=__description__,
    author=__author__,
    author_email=__author_email__,
    requires=__requires__,
    packages=__packages__
)
