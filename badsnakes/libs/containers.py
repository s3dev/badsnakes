#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the container classes for the various
            node types parsed from source code by the AST parser.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""
# pylint: disable=import-error

from badsnakes.libs.enums import Severity


class _NodeBase:
    """Private base class inherited by each AST node type container.

    Args:
        name (str, optional): Node name. Defaults to None.
        value (str | int, optional): Node value. Defaults to None.
        line (int, optional): Starting line number. Defaults to None.
        line_end (int, optional): Ending line number. Defaults to None.

    :Implementation note:
        Although many instances of this class will exist during an
        extraction, ``__slots__`` has intentionally *not* been
        implemented in either this class nor its children due to higher
        memory usage.

        When a class is inherited, the attributes are copied to its
        children, thus requiring more memory. During development
        research, using ``__slots__`` for this class *increased* memory
        usage.

    :Developer note:
        Do not add any attributes to this class, nor the child classes
        as they will propagate through into the container objects and
        trigger errors on execution.

    """

    def __init__(self,
                 *,
                 name: str=None,
                 value: str | int=None,
                 line: int=None,
                 line_end: int=None,
                 severity: Severity=Severity.OK):
        """Indicator base class initialiser."""
        self.line = line
        self.line_end = line_end
        self.name = name
        self.value = value
        self.severity = severity

    def __gt__(self, other):
        """Greater than operator implementation, based on severity."""
        if all((self, other)):
            return self.severity > other.severity
        return False

    def __lt__(self, other):
        """Less than operator implementation, based on severity."""
        if all((self, other)):
            return self.severity < other.severity
        return False

    def __str__(self):
        """Define how the object is displayed when printed.

        Primarily this is used by the :meth:`visitor.Visitor.display`
        method when displaying the extracted attributes to the terminal.

        """
        return f'{vars(self)}'

    @property
    def _log_template(self):
        """Set the generalised logging template for all containers."""
        return f'{self.severity.name},{self.line},{self.line_end},{{title}},{{text}}'

    @property
    def _report_template(self):
        """Set the generalised reporting template for all containers."""
        return f'[{self.severity.name}]: L{self.line}:{self.line_end} - {{title}}: {{text}}'

    def report_longstring(self):
        """Display a formatted view for long strings."""
        tmp = self._report_template
        trunc = f'{repr(self.value[:25])}...{repr(self.value[-25:])}'
        rpt = tmp.format(title='Long string',
                         text=f"A {len(self.value)} char string detected: {trunc}")
        print(rpt)

    def tolower(self):
        """Convert the named attribute values to lower case."""
        for attr in ('name', 'value', 'module', 'asname'):
            val = getattr(self, attr, None)
            if val and isinstance(val, str):
                setattr(self, attr, val.lower())


class Assign(_NodeBase):
    """Container class for parsed assignment nodes: ``ast.Assign``.

    :parameters:
        Refer to the docstring for the :class:`_NodeBase` class for
        argument descriptions.

    """

    def report(self):
        """Display a formatted view for assignments."""
        tmp = self._report_template
        rpt = tmp.format(title='Assignment', text=f"{self.name} = {self.value}")
        print(rpt)


class Attribute(_NodeBase):
    """Container class for parsed attribute nodes: ``ast.Attribute``.

    :parameters:
        Refer to the docstring for the :class:`_NodeBase` class for
        argument descriptions.

    """

    def report(self):
        """Display a formatted view for object attributes."""
        tmp = self._report_template
        rpt = tmp.format(title='Attribute', text=f"Use of {self.name}.{self.value} detected")
        print(rpt)


class Call(_NodeBase):
    """Container class for parsed function call nodes: ``ast.Call``.

    Args:
        module (str): Name of the module being imported.

    Refer to the docstring for the :class:`_NodeBase` class for
    additional argument descriptions.

    """

    def __init__(self, module: str=None, **kwargs):
        """Call container class initialiser."""
        super().__init__(**kwargs)
        self.module = module

    def report(self):
        """Display a formatted view for function calls."""
        tmp = self._report_template
        call = f'{self.module}.{self.name}' if self.module else self.name
        rpt = tmp.format(title='Function call', text=call)
        print(rpt)


class CodeText(_NodeBase):
    """Container class for textual code analysis.

    Args:
        reason (str): Reason the code in the module was flagged.

    Refer to the docstring for the :class:`_NodeBase` class for
    additional argument descriptions.

    """

    def __init__(self, reason: str=None, **kwargs):
        """Call container class initialiser."""
        super().__init__(**kwargs)
        self.line = 0
        self.line_end = 0
        self.reason = reason

    def report(self):
        """Display a formatted view for code text findings."""
        tmp = self._report_template
        rpt = tmp.format(title='Code text', text=self.reason)
        print(rpt)


class Constant(_NodeBase):
    """Container class for parsed constant nodes: ``ast.Constant``.

    Args:
        searchstr (str): Blacklisted keyword found in the constant.

    Refer to the docstring for the :class:`_NodeBase` class for
    additional argument descriptions.

    """

    def __init__(self, searchstr: str=None, **kwargs):
        """Call container class initialiser."""
        super().__init__(**kwargs)
        self.searchstr = searchstr

    def report(self):
        """Display a formatted view for constants.

        This method accounts for both constants as strings and arguments
        passed into function calls.

        """
        tmp = self._report_template
        if self.searchstr:
            rpt = tmp.format(title='String search',
                             text=f"'{self.searchstr}' found in {repr(self.value)}")
        else:
            rpt = tmp.format(title='Argument',
                             text=f"'{self.value}' passed into the '{self.name}' function")
        print(rpt)


class FunctionDef(_NodeBase):
    """Container class for parsed function definition nodes: ``ast.FunctionDef``.

    :parameters:
        Refer to the docstring for the :class:`_NodeBase` class for
        argument descriptions.

    """

    def report(self):
        """Display a formatted view for function definitions."""
        tmp = self._report_template
        rpt = tmp.format(title='Function definition',
                         text=f"Function named '{self.name}' detected")
        print(rpt)


class Import(_NodeBase):
    """Container class for module import nodes: ``ast.Import``.

    Args:
        module (str): Name of the module being imported.
        asname (str, optional): An import's alias if the library is
            imported using ``import mylib as _mylib``. Defaults to None.

    Refer to the docstring for the :class:`_NodeBase` class for
    additional argument descriptions.

    """

    def __init__(self, module: str, asname: str=None, **kwargs):
        """Import container class initialiser."""
        super().__init__(**kwargs)
        self.asname = asname
        self.module = module

    def report(self):
        """Display a formatted view for module imports.

        This method accounts for the various ways modules and libraries
        can be imported.

        """
        tmp = self._report_template
        if self.asname:
            module = f'{self.module}.{self.name}' if self.name else self.module
            rpt = tmp.format(title='Import',
                              text=f"import {module} as {self.asname}")
        elif self.name:
            rpt = tmp.format(title='Import',
                              text=f"from {self.module} import {self.name}")
        else:
            rpt = tmp.format(title='Import',
                              text=f"import {self.module}")
        print(rpt)
