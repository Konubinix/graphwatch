#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from graphwatch.graphwatch import main

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
