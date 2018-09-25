#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

import versioneer

version = versioneer.get_versions()["version"]
cmdclass = versioneer.get_cmdclass()

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='graphwatch',
    cmdclass=cmdclass,
    version=version,
    author="Samuel Loury",
    author_email="konubinixweb@gmail.com",
    description="A web app showing a dot graph evolutions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    zip_safe=True,
    include_package_data=True,
    package_data={'': [
        '*.js', '*.css',
    ]},
    install_requires=[
        "flexx",
        "pydot",
        "networkx",
    ],
)
