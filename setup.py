# -*- coding: utf-8 -*-
#!/bin/env python3

# Copyright (C) 2018 Gaby Launay

# Author: Gaby Launay  <gaby.launay@tutanota.com>
# URL: https://framagit.org/gabylaunay/pypyueye
# Version: 1.0

# Pypyueye is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.

# Pypyueye is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

setup(
    name='Pypyueye',
    version='1.0',
    description='Convenience wrapper around pyueye.',
    author='Gaby Launay',
    author_email='gaby.launay@tutanota.com',
    license='GPLv3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: GPLv3 License',
        'Programming Language :: Python :: 3.5',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
    ],
    keywords='ueye camera',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'samples']),
    # TODO: Add PyQt4 as requirement
    install_requires=['pyueye', 'opencv-python'],
    extras_require={},
    # setup_requires=['pytest-runner'],
    # tests_require=['pytest'],
)
