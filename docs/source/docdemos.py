#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the base logic for the user cases in
            the documentation.
"""

#%% Single module

from badsnakes.module import Module
from badsnakes.reporter import ReporterModule

path = '/var/venvs/bsnak312/lib/python3.12/site-packages/pip/_internal/main.py'

# Analyse the module.
m = Module(path=path)
m.analyse()

# Report the findings.
r = ReporterModule(modules=[m])
r.report()


# %% Multiple modules

import os
from glob import glob
from badsnakes.module import Module
from badsnakes.reporter import ReporterModule

modules = []
paths = glob(os.path.join('/var/venvs/bsnak312/lib/python3.12/site-packages/pip/_internal/', '*.py'))

# Call Module.analyse for each path and store each module object.
for path in paths:
    m = Module(path=path)
    m.analyse()
    modules.append(m)

# Report all findings at once.
r = ReporterModule(modules=modules)
r.report()

# %% Wheel

from badsnakes.collector import Collector
from badsnakes.module import Module
from badsnakes.reporter import ReporterModule

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
