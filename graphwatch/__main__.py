#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys

from graphwatch import main

main(sys.argv[1] if len(sys.argv) > 1 else "data.dot", open=False)
