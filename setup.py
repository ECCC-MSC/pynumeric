# -*- coding: utf-8 -*-
# =================================================================
#
# Copyright (c) 2017 Government of Canada
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# =================================================================

import io
import os
import re
from setuptools import Command, find_packages, setup
import sys


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        errno = subprocess.call([sys.executable,
                                 'pynumerica/tests/run_tests.py'])
        raise SystemExit(errno)


def read(filename, encoding='utf-8'):
    """read file contents"""
    full_path = os.path.join(os.path.dirname(__file__), filename)
    with io.open(full_path, encoding=encoding) as fh:
        contents = fh.read().strip()
    return contents


def get_package_version():
    """get version from top-level package init"""
    version_file = read('pynumerica/__init__.py')
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


try:
    import pypandoc
    LONG_DESCRIPTION = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError, OSError):
    print('Conversion to rST failed.  Using default (will look weird on PyPI)')
    LONG_DESCRIPTION = read('README.md')

DESCRIPTION = ('pynumerica is a Python package to read MSC URP Radar '
               'Numeric data')

if os.path.exists('MANIFEST'):
    os.unlink('MANIFEST')

setup(
    name='pynumerica',
    version=get_package_version(),
    description=DESCRIPTION.strip(),
    long_description=LONG_DESCRIPTION,
    license='GPLv3',
    platforms='all',
    keywords=' '.join([
        'numerica',
        'radar',
        'urp',
        'msc'
    ]),
    author='Meteorological Service of Canada',
    author_email='tom.kralidis@canada.ca',
    maintainer='Meteorological Service of Canada',
    maintainer_email='tom.kralidis@canada.ca',
    url='https://github.com/ECCC-MSC/pynumerica.git',
    install_requires=read('requirements.txt').splitlines(),
    packages=find_packages(exclude=['pynumerica.tests']),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'pynumerica=pynumerica:numerica_info'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ],
    cmdclass={'test': PyTest},
)
