#!/usr/bin/env

from setuptools import setup

import strif

setup(
    name="strif",
    version=strif.VERSION,
    py_modules=["strif"],
    author="Joshua Levy",
    license="Apache 2",
    url="https://github.com/jlevy/strif",
    install_requires=[],
    description=strif.DESCRIPTION,
    long_description=strif.LONG_DESCRIPTION,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
        "Topic :: Software Development",
    ],
    python_requires=">=3.6, <3.13",
)
