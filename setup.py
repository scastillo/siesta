#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from siesta import __version__

setup(
    name='siesta',
    version=__version__,
    description='Sit back, relax and enjoy of your python REST client',
    author='Sebastián Castillo Builes',
    author_email='castillobuiles@gmail.com',
    license='GPL',
    keywords='REST RESTful API HTTP web service',
    url="http://scastillo.github.com/siesta/",
    long_description="""
    Siesta is a client library to consume RESTful web services.
    """,
    packages=find_packages(),
    install_requires = ['simplejson'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
    )
