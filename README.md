
# A toolset to identify malware in Python projects.

[![PyPI - Version](https://img.shields.io/pypi/v/badsnakes?style=flat-square)](https://pypi.org/project/badsnakes)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/badsnakes?style=flat-square)](https://pypi.org/project/badsnakes)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/badsnakes?style=flat-square)](https://pypi.org/project/badsnakes)
[![PyPI - Status](https://img.shields.io/pypi/status/badsnakes?style=flat-square)](https://pypi.org/project/badsnakes)
[![Static Badge](https://img.shields.io/badge/tests-pending-orange?style=flat-square)](https://pypi.org/project/badsnakes)
[![Static Badge](https://img.shields.io/badge/code_coverage-pending-orange?style=flat-square)](https://pypi.org/project/badsnakes)
[![Static Badge](https://img.shields.io/badge/pylint_analysis-100%25-brightgreen?style=flat-square)](https://pypi.org/project/badsnakes)
[![Documentation Status](https://readthedocs.org/projects/badsnakes/badge/?version=latest&style=flat-square)](https://badsnakes.readthedocs.io/en/latest/)
[![PyPI - License](https://img.shields.io/pypi/l/badsnakes?style=flat-square)](https://opensource.org/licenses/gpl-3-0)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/badsnakes?style=flat-square)](https://pypi.org/project/badsnakes)

## Overview
The ``badsnakes`` project is a CPython library and command line utility which plugs the gap in malware analysis for Python-based malware by employing code and syntax analysis, searching for various patterns and techniques used by threat actors.

After a Python module is analysed, a report can be generated showing the module's 'classification' as *OK*, *SUSPECT* or *DANGEROUS*. If run in verbose mode, each offending statement is displayed to the terminal, along with the reason for the classification. Additionally, all *SUSPECT* and *DANGEROUS* statements can be written to a log file for further inspection and analysis.

**Note:**
This tool *will* flag false-positives, as we feel it's better to fail-safe.

Many lower-level libraries use similar techniques to threat actors by leveraging the inner-workings of the Python language beyond PEP-oriented or production-style code. As such, this is an **advisory system** designed to highlight statements which may be considered suspect, and worth investigating further. This is *not* designed to be a GO / NO-GO system.

### The Toolset
The current toolset enables malware inspection from the following input sources, either as a *library*, to be imported and wrapped by your own project(s), or as a *command line utility*.

- Directory search
- Single or multiple Python modules
- Single or multiple Python wheels

For descriptive usage, please refer to the [Using the Library](#using-the-library) or [From the Command Line](#from-the-command-line) sections.

## Installation
Likely, the easiest way to install ``badsnakes`` is using ``pip`` *after* activating your virtual environment::
    
    pip install badsnakes

This will install *both* the library and the command line utility.

Additional (older) releases can be found either at [PyPI](https://pypi.org/project/badsnakes/#history) in [GitHub Releases](https://github.com/s3dev/badsnakes/releases).

## Using the Library
The [documentation suite](https://badsnakes.readthedocs.io/en/latest/index.html) contains detailed explanation and example usage for each of the library's importable modules. For detailed documentation, usage examples and links the source code itself, please refer to the [Library API Documentation](https://badsnakes.readthedocs.io/en/latest/library.html#library-api) section of the documentation.

### From the Command Line
In addition to being an importable library, ``badsnakes`` is also a command line utility, capable of analysing, reporting and logging the following input types:

- Directories
- Single or multiple Python modules
- Single or multiple Python wheels

To call up the help menu, simply type:

    $ badsnakes --help

