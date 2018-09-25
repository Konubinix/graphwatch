#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from click_project.decorators import command, argument, flag


@command()
@argument("file", default="data.dot",
          help="The dot file to watch")
@flag("--open", help="Open a browser pointing to the live show")
def graphwatch(file, open):
    """Continuously watch a dot document to show it live"""
    from graphwatch.graphwatch import main
    main(file, open)
