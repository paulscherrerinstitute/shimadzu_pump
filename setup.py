#!/usr/bin/env python
from setuptools import setup

setup(
    name='shimadzu_pump',
    version="1.1.2",
    description="Just a Shimadzu pump controller.",
    author='Paul Scherrer Institute',
    author_email='scott.stubbs@psi.ch',
    requires=['requests'],

    packages=['shimadzu_pump']
)
