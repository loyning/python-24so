#
# Copyright 2015-2017 Rune Loyning
#
# http://github.com/loyning/python-24so
#

import os
import re

from setuptools import find_packages
from distutils.core import setup

with open(os.path.join('tfsoffice', '__init__.py')) as init:
    source = init.read()
    m = re.search("__version__ = '(\d+\.\d+(\.(\d+|[a-z]+))?)'", source, re.M)
    __version__ = m.groups()[0]

setup(
    name="python-24so",
    version=__version__,
    description='Python wrapper for the 24sevenoffice SOAP api',
    long_description="This API requires a valid account to 24SevenOffice.com and an API key",
    author='Rune Loyning',
    author_email='rune@loyning.net',
    url='http://github.com/loyning/python-24so/',
    keywords='24sevenoffice crm python',
    classifiers=[],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["suds-fc", ],
)
