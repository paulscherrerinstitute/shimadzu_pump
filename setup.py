#!/usr/bin/env python
from setuptools import setup

setup(
author='Paul Scherrer Institute',
author_email='scott.stubbs@psi.ch',
description="Just a Shimadzu pump controller.",
name='shimadzu_pump',
requires=['requests'],
packages=['shimadzu_pump'],
version="1.2.8"
)
