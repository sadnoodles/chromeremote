#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
setup(
    name="chromeremote",
    version="0.1.0",
    description="Chrome Remote Dev Tools",
    author="sadnoodles",
    author_email="sadnoodles@gmail.com",
    url="https://github.com/sadnoodles/chromeremote",
    download_url="https://github.com/sadnoodles/chromeremote/archive/v0.1.0.tar.gz",
    license="GPL",
    py_modules=["chromeremote"],
    install_requires=[
         'requests',
         'websocket-client',
    ],
    platforms="any"
)
