#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the functionality for parsing a module
            into an abstract syntax tree for analysis.

            The primary parsing work is carried out by the builtin
            :func:`ast.parse` method.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

:Example:
    Example code use::

        >>> from badsnakes.libs.parse import Parser

        >>> p = Parser()
        >>> p.parse(path='hello.py')

        # Access the abstract syntax tree.
        >>> p.ast_
        <ast.Module at 0x123456789012>

        # Access the code's text stream.
        >>> p.code
        <_io.StringIO at 0x123456789000>

"""

import ast
import io
import logging
import os

logger = logging.getLogger(__name__)


class Parser:
    """Using the ``ast`` built-in, parse a module's code into its various
    elements.

    AST elements which are used for code analysis are:

        - **Arguments**: Arguments which are passed into function calls.

          - Generally used to detect base64 strings (or the like) being
            passed into functions.

        - **Assignments**: Generally used to detect unusually long
          strings.

        - **Attributes**: Used to detect access to modules which are
          generally used for suspicious activity.

        - **Function calls**: Used to detect calls to functions which
          may be suspicious.

        - **Function declarations**: Used to detect unusual (obfuscated)
          function names in the module.

        - **Imports**: Used for capturing a module's import statements
          (or the lack thereof).

        - **Strings**: Used to capture the strings used in a module.

    """

    __slots__ = ('_ast', '_code', '_path')

    def __init__(self):
        """Module parsing class initialiser."""
        self._ast = None        # The ast.Module object.
        self._code = None       # Module code as an io.StringIO object.
        self._path = None       # Path to the module being parsed.

    @property
    def ast_(self) -> ast.Module:
        """Public accessor to the module's abstract syntax tree."""
        return self._ast

    @property
    def code(self) -> io.StringIO:
        """Public accessor to the code as a text stream."""
        return self._code

    @property
    def path(self) -> str:
        """Public accessor to the module's file path."""
        return self._path

    def display_syntax_tree(self):
        """Display the syntax tree as parsed by ``ast``."""
        print(ast.dump(self._ast, indent=4))

    def parse(self, path: str):
        """Parse a module into an abstract syntax tree.

        Additionally, a the code itself is stored into the :attr:`_code`
        attribute for additional analysis as an ``_io.StringIO`` text
        stream object.

        Args:
            path (str): Full path to the module.

        """
        self._path = os.path.realpath(path)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = f.read()
                self._code = io.StringIO(data)
                self._ast = ast.parse(data)
        except SyntaxError:
            logging.info('Not a Python code module, cannot parse: %s', path)

    def rewind(self):
        """Rewind the code stream to the beginning."""
        self._code.seek(0)
