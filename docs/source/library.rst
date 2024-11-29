
.. _library-api:

========================
Libary API Documentation
========================
The page contains simple library usage examples and the module-level 
documentation for each of the importable modules in ``badsnakes``.

.. contents::
    :local:
    :depth: 1


Use Cases
=========
To save digging through the documentation for each module and cobbling 
together what a 'standard use case' may look like, a couple have been
provided here.

.. contents::
    :local:
    :depth: 1


Analysing a single module
-------------------------
The following example demonstrates how to analyse a single module.

.. code-block:: python
   :caption: Analysing a single module

    from badsnakes.libs.module import Module
    from badsnakes.libs.reporter import ReporterModule

    path = '/path/to/project/module.py'       

    # Analyse the module.
    m = Module(path=path)
    m.analyse()

    # Report the findings.
    r = ReporterModule(modules=[m])
    r.report()

When ``r.report()`` is called, the following is displayed in the terminal:

.. code-block:: 
   :caption: Terminal output

    ---------------------------
    Module: project/module.py 
    ---------------------------

    Module classification: OK


Analysing multiple modules
--------------------------
The following example demonstrates how to analyse multiple modules. In
this case, we're looking at pip's ``pip/_internal/*.py`` modules.

.. code-block:: python
   :caption: Analysing multiple modules

    import os
    from glob import glob
    from badsnakes.libs.module import Module
    from badsnakes.libs.reporter import ReporterModule

    modules = []
    paths = glob(os.path.join('/.../site-packages/pip/_internal/', '*.py'))

    # Call Module.analyse for each path and store each module object.
    for path in paths:
       m = Module(path=path)
       m.analyse()
       modules.append(m)

    # Report all findings at once.
    r = ReporterModule(modules=modules)
    r.report()

When ``r.report()`` is called, the following (truncated output) is 
displayed in the terminal:


.. code-block:: 
   :caption: Truncated terminal output

    ----------------------------
     Module: _internal/cache.py 
    ----------------------------

    Module classification: OK

    ------------------------------------
     Module: _internal/wheel_builder.py 
    ------------------------------------

    Module classification: OK

    ---------------------------------
     Module: _internal/exceptions.py 
    ---------------------------------
    [SUSPECT]: L523:531 - Long string: A 375 char string detected: 'hashes are required in --'...' any package has a hash.)'
    [SUSPECT]: L584:587 - String search: ';' found in 'these packages do not match the hashes from the requirements file. if you have updated the package versions, please update the hashes. otherwise, examine the package contents carefully; someone may have tampered with them.'
    [DANGEROUS]: L747:747 - String search: 'pip install' found in 'pip install --force-reinstall --no-deps '

    Module classification: DANGEROUS

    ---------------------------
     Module: _internal/main.py 
    ---------------------------

    Module classification: OK

    --------------------------------
     Module: _internal/pyproject.py 
    --------------------------------

    Module classification: OK

    --------------------------------
     Module: _internal/build_env.py 
    --------------------------------
    [SUSPECT]: L111:134 - String search: '()' found in '\n                import os, site, sys\n\n                # first, drop system-sites related paths.\n                original_sys_path = sys.path[:]\n                known_paths = set()\n                for path in {system_sites!r}:\n                    site.addsitedir(path, known_paths=known_paths)\n                system_paths = set(\n                    os.path.normcase(path)\n                    for path in sys.path[len(original_sys_path):]\n                )\n                original_sys_path = [\n                    path for path in original_sys_path\n                    if os.path.normcase(path) not in system_paths\n                ]\n                sys.path = original_sys_path\n\n                # second, add lib directories.\n                # ensuring .pth file are processed.\n                for path in {lib_dirs!r}:\n                    assert not path in sys.path\n                    site.addsitedir(path)\n                '

    Module classification: SUSPECT


.. note::

    Note that long strings, the use of semi-colons and command execution
    raise *SUSPECT* or *DANGEROUS* flags. This is *not* saying ``pip`` is
    dangerous, it's only showing their programmers have used techniques
    often employed by threat actors.

    Flagging such techniques have helped us detect live malware.


Analysing a wheel
-----------------
The following example demonstrates how to analyse a Python wheel. In
this case, we're looking at our own ``badsnakes`` wheel.

.. code-block:: python
   :caption: Analysing a Python wheel

    from badsnakes.libs.collector import Collector
    from badsnakes.libs.module import Module
    from badsnakes.libs.reporter import ReporterModule

    modules = []
    path = '../dist/badsnakes-0.1.0-py3-none-any.whl'

    # Collect all non-binary files from thw wheel.
    c = Collector(paths=path)
    c.collect()

    for pkg in c.files:
       # Call Module.analyse for each path and store each module object.
       for path in pkg:
           # Analyse the module.
           m = Module(path=path)
           m.analyse()
           modules.append(m)
        
    # Report the findings.
    r = ReporterModule(modules=modules)
    r.report()

When ``r.report()`` is called, the following (truncated output) is 
displayed in the terminal:


.. code-block:: 
   :caption: Truncated terminal output

    -------------------------------------------
     Module: badsnakes-0.1.0.dist-info/LICENSE 
    -------------------------------------------

    Module classification: UNKNOWN

    -------------------------------------------------
     Module: badsnakes-0.1.0.dist-info/top_level.txt 
    -------------------------------------------------

    Module classification: UNKNOWN

    --------------------------------
     Module: badsnakes/badsnakes.py 
    --------------------------------

    Module classification: OK

    --------------------------------
     Module: badsnakes/analysers.py 
    --------------------------------
    [SUSPECT]: L555:555 - String search: ';' found in ';'

    Module classification: SUSPECT

    -------------------------------
     Module: badsnakes/reporter.py 
    -------------------------------

    Module classification: OK

    --------------------------------
     Module: badsnakes/extractor.py 
    --------------------------------

    Module classification: OK

    --------------------------------
     Module: badsnakes/argparser.py 
    --------------------------------
    [SUSPECT]: L35:41 - Long string: A 349 char string detected: 'path(s) to the python mod'...'ust be of the same type.\n'

    Module classification: SUSPECT

    --------------------------------
     Module: badsnakes/collector.py 
    --------------------------------

    Module classification: OK

    -----------------------------
     Module: badsnakes/module.py 
    -----------------------------

    Module classification: OK

    -------------------------------
     Module: badsnakes/config.toml 
    -------------------------------

    Module classification: UNKNOWN


.. note::

    Note that even our own wheel raises a *SUSPECT* flag for a long string
    found in the ``argparser`` module. This is not to say the module is 
    unsafe, but rather a warning for the user to be aware of.

    Additionally, notice the *UNKNOWN* classifications. This classification
    is used for plain-text files which could not be parsed by the ``ast``
    parser, and are therefore *not* Python modules.


Module Documentation
====================

In addition to the module-level documentation, most of the public 
classes and/or methods come with one or more usage examples and access
to the source code itself.

.. toctree:: 
   :caption: Links to module-level documentation
   :maxdepth: 1

   analysers
   badsnakes
   collector
   config
   containers
   enums
   extractor
   logger
   module
   parser
   reporter
   utilities
