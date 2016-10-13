# -*- coding: utf-8 -*-
"""Reloadr - Python library for hot code reloading
(c) 2015-2016 Hugo Herter
"""

import os

from setuptools import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with open('README.rst') as file:
    long_description = file.read()

setup(name='Reloadr',
      version='0.2.0',
      description='Hot code reloading tool for Python',
      long_description=long_description,
      author='Hugo Herter',
      author_email='git@hugoherter.com',
      url='https://github.com/hoh/reloadr',
      py_modules=['reloadr'],
      scripts=['reloadr.py'],
      data_files=[],
      install_requires=[
          'redbaron',
          ],
      license='LGPLv3',
      platform='any',
      keywords="reload hot code reloading",
      classifiers=['Development Status :: 2 - Pre-Alpha',
                   'Programming Language :: Python :: 3.4',
                   'Operating System :: POSIX :: Linux',
                   'Intended Audience :: Developers',
                   ],
      )
