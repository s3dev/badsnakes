#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module contains the original development code for the
            code analyser.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""

# import ast
import os
import sys
# Put the root project directory in sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../'))
# locals
from badsnakes import Module

# %% File getter

PATH = os.path.join(sys.path[0], 'meta/research/samples')

files = {
         'cookie_stealer': os.path.join(PATH, 'cookie_stealer.py'),
         'hello': os.path.join(PATH, 'hello.py'),
         'ihatemyself': os.path.join(PATH, 'ihatemyself.py'),
         'inferior': os.path.join(PATH, 'inferior.py'),
         'keylogger': os.path.join(PATH, 'keylogger.py'),
         'replica': os.path.join(PATH, 'Replica.py'),
         'screenlogger': os.path.join(PATH, 'screenlogger.py'),
         'silvar': os.path.join(PATH, 'silvar_rware.py'),
         'stealer': os.path.join(PATH, 'stealer8.py'),
         'various': os.path.join(PATH, 'various.py'),
         'mw01': os.path.join(PATH, 'mw01.unknown'),
         'mw02': os.path.join(PATH, 'mw02.unknown'),
         'mw03': os.path.join(PATH, 'mw03.unknown'),
         'mw04': os.path.join(PATH, 'mw04.unknown'),
         'mw05': os.path.join(PATH, 'mw05.unknown'),
         'mw06': os.path.join(PATH, 'mw06.unknown'),
         'mw07': os.path.join(PATH, 'mw07.unknown'),
         'socketclient': os.path.join(PATH, 'file-client.py'),
         'socketserver': os.path.join(PATH, 'file-server.py'),
         '---': '---',
         'convert': '/var/devmt/py/utils4_1.6.0/utils4/convert.py',     # Non-malware
         'crypto': '/var/devmt/py/utils4_1.6.0/utils4/crypto.py',       # Non-malware
         'cutils': '/var/devmt/py/utils4_1.6.0/utils4/cutils.py',       # Non-malware
         'filesys': '/var/devmt/py/utils4_1.6.0/utils4/filesys.py',         # Non-malware
         'registry': '/var/devmt/py/utils4_1.6.0/utils4/registry.py',         # Non-malware
         'srccheck': '/var/devmt/py/utils4_1.6.0/utils4/srccheck.py',         # Non-malware
         'validation': '/var/devmt/py/utils4_1.6.0/utils4/validation.py',         # Non-malware
         'utils': '/var/devmt/py/utils4_1.6.0/utils4/utils.py',         # Non-malware
         'notes': '../meta/research/NOTES',                             # Trigger an error
         'readme': os.path.join(PATH, 'README'),                        # Trigger an error
         '----': '----',
         'assign': os.path.join(PATH, 'assign.py'),                       # Single line len(body) == 1
         'print': os.path.join(PATH, 'print.py'),                       # Single line len(body) == 1
         '-----': '----',
         'badsnakes': '../badsnakes/badsnakes.py',
         'containers': '../badsnakes/containers.py',
         'analysers': '../badsnakes/analysers.py',
         'extractor': '../badsnakes/extractor.py',
         'logger': '../badsnakes/logger.py',
         'module': '../badsnakes/module.py',
         'parser': '../badsnakes/parser.py',
        }


# %% Run the analyser with Module (v2)

from badsnakes.reporter import ReporterModule

NAME = 'mw07'

m = Module(path=files.get(NAME))
m.analyse()
# m.display()
# m.display_syntax_tree()

# print('\n[DEBUG]: Body items:', len(m.ast_.body))


ReporterModule(modules=m).report()
# ReporterModule(modules=m).report_classification_only()

# %% Logger

import os
from datetime import datetime as dt
from badsnakes.logger import Logger

fpath = os.path.join(os.path.expanduser('~/Desktop'), f"test_{dt.now().strftime('%Y%m%dT%H%M%S')}.log")

Logger(path=fpath, modules=[m]).write()
