#!/usr/bin/env python
from setuptools import setup

setup(
    name='shimadzu_pump',
    version="0.0.3",
    description="Just a Shimadzu pump controller.",
    author='Paul Scherrer Institute',
    author_email='andrej.babic@psi.ch',
    requires=['requests'],

    packages=['shimadzu_pump']
)
