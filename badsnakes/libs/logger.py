#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the *file-based* reporting
            functionality for the project. Terminal-based reporting is
            handled by the :mod:`badsnakes.libs.reporter` module.

            Each ``_LogTemplate*`` class is responsible for the
            formatting of each AST node class. Whereas the primary caller
            :class:`Logger` class controls the file creation and writing
            functionalities.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

:Example:
            Create a log file for a given module, or modules::

                >>> from badsnakes import Module
                >>> from badsnakes.libs.logger import Logger

                # Analyse a Python module.
                >>> m = Module(path='/path/to/millworker.py')
                >>> m.analyse()

                # Create the log file.
                >>> l = Logger(path='/path/to/millworker.log', modules=[m])
                >>> l.write()

"""

# Enable type hinting
from __future__ import annotations

import os


class Logger:
    """Write module findings to a log file.

    Args:
        path (str): Full path to the log file to be created.
        modules (list[module.Module] | tuple[module.Module]): A list or
            tuple containing :class:`badsnakes.libs.module.Module`
            objects containing findings to be written to a log file.

    """

    _HEADER = 'severity,module,line_start,line_end,title,text'

    def __init__(self, path: str, modules: list[module.Module] | tuple[module.Module]):  # noqa # pylint: disable=undefined-variable
        """Logger class initialiser."""
        self._fp = path
        self._modules = modules if isinstance(modules, (list, tuple)) else [modules]
        self._tmps = None  # Logging templates.
        self._setup()

    def write(self):
        """Write log entries for all modules.

        :Logic:
            For each module passed on instantiation, create a logging
            template parent-class, based on the module's name.

            Suspect findings are written first, followed by dangerous
            findings.

        """
        for module in self._modules:
            self._tmps = _LogTemplates(module_name=module.name_and_parent)
            self._write_suspect(module=module)
            self._write_dangerous(module=module)

    def _setup(self):
        """Create the new log file, if it does not already exist."""
        if not os.path.exists(self._fp):
            with open(self._fp, 'w', encoding='utf-8') as f:
                f.write(f'{self._HEADER}\n')

    def _write(self, text: str):
        """Generalised log entry writer.

        Args:
            text (str): Delimited text string to be written to the log.

        """
        if text:
            with open(self._fp, 'a', encoding='utf-8') as f:
                f.write(f'{text}\n')

    def _write_dangerous(self, module: module.Module):  # noqa # pylint: disable=undefined-variable
        """Write a module's *dangerous* findings to the log file.

        Args:
            module (module.Module): Module for which the log entries are
                to be written.

        :Logic:
            For each AST node class, obtain the associated log template
            sub-class from :class:`_LogTemplates`, using the node class'
            ``.name`` property.

            Using the AST-specific log template, write the dangerous
            findings to the log file created on logger instantiation.

        """
        for nc in module.nodeclasses:
            logger = getattr(self._tmps, nc.name, None)
            if logger:
                for node in nc.analyser.dangerous:
                    self._write(logger.entry(node))
                for node in nc.analyser.dangerous_longstring:
                    self._write(logger.entry_longstring(node))

    def _write_suspect(self, module: module.Module):  # noqa # pylint: disable=undefined-variable
        """Write a module's *suspect* findings to the log file.

        Args:
            module (module.Module): Module for which the log entries are
                to be written.

        :Logic:
            For each AST node class, obtain the associated log template
            sub-class from :class:`_LogTemplates`, using the node class'
            ``.name`` property.

            Using the AST-specific log template, write the suspect
            findings to the log file created on logger instantiation.

        """
        for nc in module.nodeclasses:
            logger = getattr(self._tmps, nc.name, None)
            if logger:
                for node in nc.analyser.suspect:
                    self._write(logger.entry(node))
                for node in nc.analyser.suspect_longstring:
                    self._write(logger.entry_longstring(node))


# %% Related private class implementations.

class _LogTemplates:
    """Private wrapper class for all logging templates."""

    __slots__  = ('arguments',
                  'assignments',
                  'attributes',
                  'calls',
                  'codetext',
                  'constants',
                  'functiondefs',
                  'imports')

    def __init__(self, module_name: str):
        self.arguments = _LogTemplateArguments(module_name=module_name)
        self.assignments = _LogTemplateAssignment(module_name=module_name)
        self.attributes = _LogTemplateAttribute(module_name=module_name)
        self.calls = _LogTemplateCall(module_name=module_name)
        self.codetext = _LogTemplateCodeText(module_name=module_name)
        self.constants = _LogTemplateConstant(module_name=module_name)
        self.functiondefs = _LogTemplateFunctionDef(module_name=module_name)
        self.imports = _LogTemplateImport(module_name=module_name)


class _LogTemplateBase:
    """Private template logging base class.

    This class provides the :meth:`_populate` method to the sub-classes,
    which is used to build the log entry.

    Args:
        module_name (str): Name of the module being logged. This name is
            written to the 'module' field of the log file.

    """

    _BASE = '{severity},{module},{line_start},{line_end},{title},"{text}"'
    _TITLE = ''

    def __init__(self, module_name: str):
        """Log templates base class initialiser."""
        self._name = module_name

    def entry_longstring(self, node: object):
        """Generate an entry for a long string.

        Args:
            node (object): AST node container from which the severity and
                line numbers are obtained.

        Note:
            Long strings are truncated to the leading and trailing 25
            characters to preserve brevity.

        Returns:
            str: The complete, formatted entry to be written to the log
            file.

        """
        trunc = f'{repr(node.value[:25])}...{repr(node.value[-25:])}'
        text = f"A {len(node.value)} char string detected: {trunc}"
        return self._populate(node=node, text=text, title='Long string')

    def _populate(self, node: object, text: str, title: str=None) -> str:
        """Generate a node-specific log entry.

        Args:
            node (object): AST node container from which the severity and
                line numbers are obtained.
            text (str): Text to be written to the 'text' field of the
                log file.
            title (str, optional): Title to be written to the 'title'
                field of the log file. If provided, this argument
                overrides the ``_TITLE`` attribute of the node-specific
                logging class. Defaults to None.

        Returns:
            str: The complete, formatted entry to be written to the log
            file.

        """
        title = title if title else self._TITLE
        return self._BASE.format(severity=node.severity.name,
                                 module=self._name,
                                 line_start=node.line,
                                 line_end=node.line_end,
                                 title=title,
                                 text=text)


class _LogTemplateArguments(_LogTemplateBase):
    """``Constant`` node class specific logging template class."""

    _TITLE = 'Argument'

    def entry(self, node: containers.Constant) -> str:  # noqa # pylint: disable=undefined-variable
        """Generate a node-specific log entry.

        Args:
            node (containers.Constant): A :class:`badsnakes.libs.containers.Constant`
                object containing the values from which the log entry is
                derived.

        Returns:
            str: The complete, formatted entry to be written to the log
            file.

        """
        text = f"'{node.value}' passed into the '{node.name}' function"
        return self._populate(node=node, text=text)


class _LogTemplateAssignment(_LogTemplateBase):
    """``Assignment`` node class specific logging template class."""

    _TITLE = 'Assignment'

    def entry(self, node: containers.Assign) -> str:  # noqa # pylint: disable=undefined-variable
        """Generate a node-specific log entry.

        Args:
            node (containers.Assign): A :class:`badsnakes.libs.containers.Assign`
                object containing the values from which the log entry is
                derived.

        Returns:
            str: The complete, formatted entry to be written to the log
            file.

        """
        text = f"{node.name} = {node.value}"
        return self._populate(node=node, text=text)


class _LogTemplateAttribute(_LogTemplateBase):
    """``Attribute`` node class specific logging template class."""

    _TITLE = 'Attribute'

    def entry(self, node: containers.Attribute) -> str:  # noqa # pylint: disable=undefined-variable
        """Generate a node-specific log entry.

        Args:
            node (containers.Attribute): A :class:`badsnakes.libs.containers.Attribute`
                object containing the values from which the log entry is
                derived.

        Returns:
            str: The complete, formatted entry to be written to the log
            file.

        """
        text = f"Use of {node.name}.{node.value} detected"
        return self._populate(node=node, text=text)


class _LogTemplateCall(_LogTemplateBase):
    """``Call`` node class specific logging template class."""

    _TITLE = 'Function call'

    def entry(self, node: containers.Call) -> str:  # noqa # pylint: disable=undefined-variable
        """Generate a node-specific log entry.

        Args:
            node (containers.Call): A :class:`badsnakes.libs.containers.Call`
                object containing the values from which the log entry is
                derived.

        Returns:
            str: The complete, formatted entry to be written to the log
            file.

        """
        text = f'{node.module}.{node.name}' if node.module else node.name
        return self._populate(node=node, text=text)


class _LogTemplateCodeText(_LogTemplateBase):
    """``CodeText`` node class specific logging template class."""

    _TITLE = 'CodeText'

    def entry(self, node: containers.CodeText) -> str:  # noqa # pylint: disable=undefined-variable
        """Generate a node-specific log entry.

        Args:
            node (containers.CodeText): A :class:`badsnakes.libs.containers.CodeText`
                object containing the values from which the log entry is
                derived.

        Returns:
            str: The complete, formatted entry to be written to the log
            file.

        """
        return self._populate(node=node, text=node.reason)


class _LogTemplateConstant(_LogTemplateBase):
    """``Constant`` node class specific logging template class."""

    _TITLE = 'String search'

    def entry(self, node: containers.Constant) -> str:  # noqa # pylint: disable=undefined-variable
        """Generate a node-specific log entry.

        Args:
            node (containers.Constant): A :class:`badsnakes.libs.containers.Constant`
                object containing the values from which the log entry is
                derived.

        Returns:
            str: The complete, formatted entry to be written to the log
            file.

        """
        text=f"'{node.searchstr}' found in {repr(node.value)}"
        return self._populate(node=node, text=text)


class _LogTemplateFunctionDef(_LogTemplateBase):
    """``FunctionDef`` node class specific logging template class."""

    _TITLE = 'Function definition'

    def entry(self, node: containers.FunctionDef) -> str:  # noqa # pylint: disable=undefined-variable
        """Generate a node-specific log entry.

        Args:
            node (containers.FunctionDef): A :class:`badsnakes.libs.containers.FunctionDef`
                object containing the values from which the log entry is
                derived.

        Returns:
            str: The complete, formatted entry to be written to the log
            file.

        """
        text = f"Function named '{node.name}' detected"
        return self._populate(node=node, text=text)


class _LogTemplateImport(_LogTemplateBase):
    """``FunctionDef`` node class specific logging template class."""

    _TITLE = 'Import'

    def entry(self, node: containers.Import) -> str:  # noqa # pylint: disable=undefined-variable
        """Generate a node-specific log entry.

        Args:
            node (containers.Import): A :class:`badsnakes.libs.containers.Import`
                object containing the values from which the log entry is
                derived.

        Returns:
            str: The complete, formatted entry to be written to the log
            file.

        """
        if node.asname:
            module = f'{node.module}.{node.name}' if node.name else node.module
            text = f"import {module} as {node.asname}"
        elif node.name:
            text = f"from {node.module} import {node.name}"
        else:
            text = f"import {node.module}"
        return self._populate(node=node, text=text)
