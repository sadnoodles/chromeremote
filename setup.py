#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

long_description = """
Chrome Remote is a tool for remote debug with Chrome. 
It can be used for web spider, automatic testing, XSS detection etc.

See more from github https://github.com/sadnoodles/chromeremote.
"""

setup(
    name="chromeremote",
    version="0.2.2",
    description="Chrome Remote Dev Tools",
    long_description=long_description,
    author="sadnoodles",
    author_email="sadnoodles@gmail.com",
    url="https://github.com/sadnoodles/chromeremote",
    download_url="https://github.com/sadnoodles/chromeremote/archive/v0.2.0.tar.gz",
    license="GPL",
    py_modules=["chromeremote"],
    install_requires=[
         'requests',
         'websocket-client',
    ],
    platforms="any"
)
