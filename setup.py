#!/usr/bin/env python

from setuptools import setup

import reloadr

setup(
    name='reloadr',
    version=reloadr.__version__,
    description='Fast and simple hot code reloader tool.',
    long_description=reloadr.__doc__,
    author=reloadr.__author__,
    author_email='pypi@hugoherter.com',
    url='https://github.com/hoh/Reloadr/',
    py_modules=['reloadr'],
    scripts=['reloadr.py'],
    license='Apache',
    platforms='any',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3.4',
        ],
    )
