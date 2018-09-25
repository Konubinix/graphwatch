#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='graphwatch',
    version="0.0.0",
    author="Samuel Loury",
    author_email="konubinixweb@gmail.com",
    description="A web app showing a dot graph evolutions.",
    packages=find_packages(),
    zip_safe=True,
    include_package_data=True,
    install_requires=[
        "flexx",
        "pydot",
        "networkx",
    ],
)
