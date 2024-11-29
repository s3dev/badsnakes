#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides abstract syntax tree node visitation
            and attribute extraction functionality.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

:Example:
    Example code use::

        >>> from badsnakes.libs.parser import Parser
        >>> from badsnakes.libs.extractor import Extractor

        >>> p = Parser()
        >>> e = Extractor()
        >>> p.parse(path='hello.py')
        >>> e.extract(node=p.ast_)

        # Display the extracted nodes.
        >>> e.display()

"""
# pylint: disable=import-error

import ast
import logging
# locals
from badsnakes.libs.containers import (Assign,
                                       Attribute,
                                       Call,
                                       Constant,
                                       FunctionDef,
                                       Import)

logger = logging.getLogger(__name__)


class Extractor(ast.NodeVisitor):
    """Inspect, extract and store relevant AST node attributes."""

    def __init__(self):
        """Node visitor class initialiser."""
        super().__init__()
        self._args = []         # Storage for ast.Constant used as function arguments.
        self._assigns = []      # Storage for ast.Assign
        self._attrs = []        # Storage for ast.Attribute
        self._calls = []        # Storage for ast.Call
        self._constants = []    # Storage for ast.Constant
        self._funcdefs = []     # Storage for ast.FunctionDef
        self._imports = []      # Storage for ast.Import and ast.ImportFrom
        self._docs = set()      # Extracted docstrings used to filter constants.

    def display(self, name: str=None):
        """Display the extracted contents.

        The extracted attributes for each of the following AST nodes are
        displayed here:

            - ast.Assign
            - ast.Attribute
            - ast.Call
            - ast.Constants
            - ast.FunctionDef
            - ast.Import
            - ast.ImportFrom

        Args:
            name (str, optional): Name of the Python module being
                displayed. Defaults to None.

        """
        title = f'Extracted attributes from: {name}'
        sep = '-' * len(title)
        # This is intentionally verbose for easy readability and maintenance.
        print('',
              sep,
              title,
              sep,
              '',
              'Function arguments:',
              *(n for n in self._args),
              '',
              'Assignments:',
              *(n for n in self._assigns),
              '',
              'Attributes:',
              *(n for n in self._attrs),
              '',
              'Function calls:',
              *(n for n in self._calls),
              '',
              'Constants:',
              *(n for n in self._constants),
              '',
              'Function definitions:',
              *(n for n in self._funcdefs),
              '',
              'Imports:',
              *(n for n in self._imports),
              sep='\n')

    def extract(self, node: ast.Module):
        """Extract and store relevant attributes from a parsed AST.

        This method is an alias for the :meth:`ast.NodeVisitor.visit`
        which is called directly, after the docstrings have been
        extracted.

        Args:
            node (ast.Module): Starting node to be visited from which
                attributes are to be extracted.

        """
        if node:
            self._extract_docstrings(node=node)
            self.visit(node=node)

    def visit_Assign(self, node: ast.Assign):
        """Extract attributes of interest from ``ast.Assign`` nodes.

        Generally, the assignments are used by the analyser to detect
        (very) long strings, or suspicious module or function aliasing.

        For example:

            - [A very very long string which may be base64 encoded code]
            - A URL including 'http'
            - cexe = exec
            - lave = eval
            - _i = __import__

        Args:
            node (ast.Assign): A node of type ``ast.Assign``.

        """
        # Capture assigned values. (e.g.: callables, constants, tuple assignments)
        for target, value in zip(node.targets, [node.value]):
            # Assignment of a callable. (e.g.: c = __import__('builtins').compile)
            if isinstance(value, ast.Attribute):
                if isinstance(value.value, ast.Call):
                    a = Assign(name=getattr(target, 'id', None) or getattr(target, 'attr', None),
                               value=value.attr,
                               line=node.lineno,
                               line_end=node.end_lineno)
                    self._assigns.append(a)
            # Assignment of a 'normal' constant. (e.g.: x = 'a string')
            elif isinstance(value, ast.Constant):
                a = Assign(name=getattr(target, 'id', None),
                           value=value.value,
                           line=node.lineno,
                           line_end=node.end_lineno)
                self._assigns.append(a)
            elif isinstance(value, ast.Tuple):
                if hasattr(target, 'elts'):
                    # Assignment from tuple unpacking. (e.g.: a, b = 'thingA', 'thingB')
                    for t_elt, v_elt in zip(target.elts, value.elts):
                        a = Assign(name=getattr(t_elt, 'id', None),
                                   value=getattr(v_elt, 'value', None),
                                   line=node.lineno,
                                   line_end=node.end_lineno)
                        self._assigns.append(a)
                else:
                    # Assignment from tuple packing. (e.g.: a = ('thingA', 'thingB'))
                    for v in value.elts:
                        a = Assign(name=(getattr(target, 'id', None)
                                         or getattr(target, 'attr', None)),
                                   value=getattr(v, 'value', None),
                                   line=node.lineno,
                                   line_end=node.end_lineno)
                        self._assigns.append(a)
        self.generic_visit(node=node)

    def visit_Attribute(self, node: ast.Attribute):
        """Extract attributes of interest from ``ast.Attribute`` nodes.

        For example:

            - ``__builtins__.__getattribute__``
            - ``ctypes.windll``
            - ``os.system``

        Args:
            node (ast.Attribute): A node of type ``ast.Attribute``.

        """
        if isinstance(node.value, ast.Name):
            a = Attribute(name=node.value.id,
                          value=node.attr,
                          line=node.value.lineno,
                          line_end=node.end_lineno)
            self._attrs.append(a)
        self.generic_visit(node=node)

    def visit_Call(self, node: ast.Call):
        """Extract attributes of interest from ``ast.Call`` nodes.

        Generally, function calls are used by the analyser to detect
        calls to functions which are generally considered unsafe, or
        used for suspicious activity.

        Additionally, any arguments into these function calls are stored
        into the :attr:`_args` class attribute, to be later added to the
        ``Module.arguments`` object.

        For example:

            - Calls ``compile``, ``exec`` or ``eval``
            - Disguised imports using ``__import__``
            - Calls to ``requests.post``

        Args:
            node (ast.Call): A node of type ``ast.Call``.

        """
        # Function calls which are attributes of objects. (e.g.: str.join())
        if isinstance(node.func, ast.Attribute):
            c = Call(name=node.func.attr,
                     module=getattr(node.func.value, 'id', None),
                     line=node.lineno,
                     line_end=node.end_lineno)
            self._calls.append(c)
        # Function calls. (e.g.: print(), or test1())
        elif isinstance(node.func, ast.Name):
            c = Call(name=node.func.id,
                     line=node.lineno,
                     line_end=node.end_lineno)
            self._calls.append(c)
            # Capture function call arguments.
            for arg in node.args:
                if isinstance(arg, ast.Constant):
                    cst = Constant(name=node.func.id,
                                   value=arg.value,
                                   line=node.lineno,
                                   line_end=node.end_lineno)
                    self._args.append(cst)
        self.generic_visit(node=node)

    def visit_Constant(self, node: ast.Constant):
        """Extract attributes of interest from ``ast.Constant`` nodes.

        Generally, the constants of interest here are *strings*. The
        extracted strings will be compared against the blacklisted
        strings to determine if any suspicious activities are being
        attempted.

        :Docstrings:
            Often times, a docstring containing benign text such as a
            semi-colon or the term 'execute' can flag a module as
            dangerous during a string search.

            Because of this, the AST is walked to collect and store all
            docstrings when :meth:`extract` method is called. A constant
            node is only stored by this method for analysis if the
            constant's value was *not* found in the stored docstrings.
            For further rationale on this, please refer to the
            :meth:`_extract_docstrings` method.

        For example:

            - Calls to cmd.exe or powershell
            - References to Bitcoin or other payment demands
            - Windows registry key paths

        Args:
            node (ast.Constant): A node of type ``ast.Constant``.

        """
        if node.value not in self._docs:  # i.e.: Verify string is not a docstring.
            c = Constant(value=node.value, line=node.lineno, line_end=node.end_lineno)
            self._constants.append(c)
        self.generic_visit(node=node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Extract attributes of interest from ``ast.FunctionDef`` nodes.

        Generally, the analyser will use these nodes in search of
        obfuscated function names, indicating suspicious activity.

        For example:

            - ``_``
            - ``__``
            - ``_0xb1``
            - ``_00OO00OO``
            - ``_01001001``

        Args:
            node (ast.FunctionDef): A node of type ``ast.FunctionDef``.

        """
        f = FunctionDef(name=node.name, line=node.lineno, line_end=node.end_lineno)
        self._funcdefs.append(f)
        self.generic_visit(node=node)

    def visit_Import(self, node: ast.Import):
        """Extract attributes of interest from ``ast.Import`` nodes.

        Generally, the analyser will use these nodes in search of
        module imports which may indicate suspicious activity.

        For example:

            - import requests
            - import winreg
            - import ctypes as ct
            - import win32api as _win32api
            - import win32con as _win32con

        Args:
            node (ast.Import): A node of type ``ast.Import``.

        """
        for n in node.names:
            i = Import(module=n.name, asname=n.asname, line=n.lineno, line_end=n.end_lineno)
            self._imports.append(i)
        self.generic_visit(node=node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Extract attributes of interest from ``ast.ImportFrom`` nodes.

        Generally, the analyser will use these nodes in search of
        module imports which may indicate suspicious activity.

        For example:

            - from win32api import SetFileAttributes
            - from win32con import SRCAND, FILE_ATTRIBUTE_HIDDEN
            - from win32file import CreateFileW, WriteFile, CloseHandle

        Args:
            node (ast.ImportFrom): A node of type ``ast.ImportFrom``.

        """
        for n in node.names:
            i = Import(module=node.module,
                       name=n.name,
                       asname=n.asname,
                       line=n.lineno,
                       line_end=n.end_lineno)
            self._imports.append(i)
        self.generic_visit(node=node)

    def _extract_docstrings(self, node: ast.Module):
        """Collect all docstrings in the module and store.

        Args:
            node (ast.Module): Top-level AST node to be searched.

        The extracted (uncleaned) docstrings are stored into the
        :attr:`_docs` attribute. A constant is only tested if the value
        is *not* in the ``_docs`` attribute.

        :Rationale:
            Extracting and storing docstrings lets us put simple strings
            such as ``';'`` and ``'()'`` in ``config.toml`` under the
            ``[analyser.constant.dangerous]`` and
            ``[analyser.constant.suspect]`` tables without having a
            false-positive trigger for the string being somewhere in the
            docstring.

        """
        fns = [n for n in ast.walk(node)
               if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.Module))]
        self._docs = {ast.get_docstring(f, clean=False) for f in fns}
