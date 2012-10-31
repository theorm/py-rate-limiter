#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import rate_limiter

setup(
    name=rate_limiter.__title__,
    version=rate_limiter.__version__,
    description='Calculate hourly rate limit.',
    author=rate_limiter.__author__,
    author_email=rate_limiter.__email__,
    url='http://github.com/theorm/py-rate-limiter/',
    packages=['rate_limiter'],
    install_requires=[],
    tests_require=["nose"],
    test_suite="tests",
    classifiers=(
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    )
)