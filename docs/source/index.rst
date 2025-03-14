===============================
badsnakes Library Documentation
===============================

.. contents:: Page Contents
    :local:
    :depth: 1


Overview
========
The ``badsnakes`` project is a CPython library and command line utility
which plugs the gap in malware analysis for Python-based malware by
employing code and syntax analysis, searching for various patterns and
techniques used by threat actors.

After a Python module is analysed, a report can be generated showing the
module's 'classification' as *OK*, *SUSPECT* or *DANGEROUS*. If run in 
verbose mode, each offending statement is displayed to the terminal.
Additionally, all *SUSPECT* and *DANGEROUS* statements can be written to
a log file for further inspection and analysis.

.. note::

    This tool *will* flag false-positives, as we feel it's better to 
    fail-safe.

    Many lower-level libraries use similar techniques to threat actors 
    by leveraging the inner-workings of the Python language beyond 
    PEP-oriented or production-style code. As such, this is an 
    **advisory system** designed to highlight statements which may be
    considered suspect, and worth investigating further.


Toolset
-------
The current toolset enables malware inspection from the following input 
sources, either as a *library*, to be imported and wrapped by your own 
project(s), or as a *command line utility*.

- Directory search
- Single or multiple Python modules
- Single or multiple Python wheels

For descriptive usage, please refer to the :ref:`using-the-library` or 
:ref:`from-the-command-line` sections.

If you have any questions that are not covered by this documentation, or
if you spot any bugs, issues or have any recommendations, please feel free
to :ref:`contact us <contact-us>` or raise an issue on `GitHub`_.


Installation
============
The easiest way to install ``badsnakes`` is using ``pip`` *after* activating
your virtual environment::
    
    pip install badsnakes

This will install *both* the library and the command line utility.

Additional (older) releases can be found either at `PyPI`_ or in 
`GitHub Releases`_.


.. _using-the-library:

Using the Library
=================
This documentation suite contains detailed explanation and example usage 
for each of the library's importable modules. For detailed documentation, 
usage examples and links the source code itself, please refer to the 
:ref:`library-api` page.

If there is a specific module or method which you cannot find, a 
**search** field is built into the navigation bar to the left.


.. _from-the-command-line:

From the Command Line
---------------------
In addition to being an importable library, ``badsnakes`` is also a
command line utility, capable of analysing, reporting and logging the
following input types:

- Directories
- Single or multiple Python modules
- Single or multiple Python wheels

To call up the help menu, simply type::

    $ badsnakes --help


.. _troubleshooting:

Troubleshooting
===============
No guidance at this time.


Documentation Contents
======================
.. toctree::
    :maxdepth: 1

    library
    changelog
    contact


Indices and Tables
==================
* :ref:`genindex`
* :ref:`modindex`


.. rubric:: Footnotes

.. _GitHub Releases: https://github.com/s3dev/badsnakes/releases
.. _GitHub: https://github.com/s3dev/badsnakes
.. _PyPI: https://pypi.org/project/badsnakes/#history


|lastupdated|

