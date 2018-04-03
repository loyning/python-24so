# -*- coding: utf-8 -*-

from .client import Client  # noqa
# for backwards compability
from .soap import TwentyFour  # noqa

__title__ = 'tfsoffice'
__version__ = '0.1.981'
__copyright__ = 'Copyright 2017 Dataselskapet AS'
__author__ = 'rune@loyning.net'
__all__ = ['TwentyFour', 'Client']  # noqa

RELATED_DOCS_TEXT = "See https://github.com/loyning/python-24so \
for usage examples."
