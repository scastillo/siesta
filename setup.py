#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from siesta import __version__

fd = open("README.md")
long_description = fd.read()
fd.close()

setup(
    name='siesta',
    version=__version__,
    description='Sit back, relax and enjoy of your python REST client',
    author='Sebastián Castillo Builes',
    author_email='castillobuiles@gmail.com',
    license='BSD',
    keywords='REST RESTful API HTTP web service',
    url="",
    long_description=long_description,
    packages=find_packages(),
    install_requires = ['simplejson'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
    )
