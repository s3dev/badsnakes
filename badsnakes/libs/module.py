#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module implements the :class:`Module` class object which
            provides the primary parsing, extraction, analysis and
            results container for the project.

            The :class:`Module` class is the object which stores the
            relevant statements extracted from the AST and their analysis
            results. Each AST node class contained in the
            :class:`_NodeClasses` class (accessed via the
            :attr:`Module.nodeclasses` property) contains an iterator
            which enables the node classes to be called in a controlled
            loop and analysed.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

:Example:
            To perform analysis on a Python module::

                >>> from badsnakes import Module

                # Create and analyse
                >>> m = Module(path='spam.py')
                >>> m.analyse()

                # Display the raw findings (debugging)
                >>> m.display()

"""
# pylint: disable=import-error

import io
import logging
import os
# locals
from badsnakes.libs.analysers import (ArgumentAnalyser,
                                      AttributeAnalyser,
                                      AssignmentAnalyser,
                                      CallAnalyser,
                                      CodeTextAnalyser,
                                      ConstantAnalyser,
                                      FunctionDefAnalyser,
                                      ImportAnalyser)
from badsnakes.libs.enums import Severity
from badsnakes.libs.extractor import Extractor
from badsnakes.libs.parser import Parser


class Module:
    """Primary container class for the Python module.

    Args:
        path (str): Full path to the module to be parsed and analysed.

    The :attr:`nodeclasses` property provides access to each of the
    relevant AST node class types which were parsed from the source code.
    When populated, each node class will be a list of
    :mod:`badsnakes.libs.containers` objects containing the analyser and
    detail extracted from each node.

    On class instantiation, during initialisation, the following takes
    place:

        - Create instances of the following tools:

          - :class:`_NodeClasses`
          - :class:`~badsnakes.libs.parser.Parser`
          - :class:`~badsnakes.libs.extractor.Extractor`

        - Call the :meth:`_init` method of this call to perform the
          following tasks:

          - Set the module's filepath and filename.
          - Call the following methods to prepare for analysis:

            - :meth:`_parse`
            - :meth:`_extract`
            - :meth:`_build`

    Once complete, the module has been prepared for analysis and
    reporting.

    """

    __slots__ = ('_clf', '_name', '_path', '_extractor', '_nc', '_parser')

    def __init__(self, path: str):
        """Module class initialiser."""
        self._path = path
        self._clf = Severity.UNKNOWN    # Module classification.
        self._name = None               # Python module filename.
        self._extractor = Extractor()
        self._nc = _NodeClasses()
        self._parser = Parser()
        self._init()

    def __iter__(self):
        """Module class iterator.

        When the :class:`Module` class is iterated, the
        :attr:`nodeclasses` are returned.

        """
        yield from self._nc

    @property
    def ast_(self):
        """Public accessor to the module's parsed syntax tree.

        Syntax tree parsing is provided by the ``ast`` builtin. This
        property is a direct accessor to the return value from the
        :func:`ast.parse` method.

        """
        return self._parser.ast_

    @property
    def classification(self):
        """Accessor to the module's maximum severity classification."""
        return self._clf

    @property
    def code(self) -> io.StringIO:
        """Public accessor to the textual codebase.

        As the code is a stream object, the cursor (memory pointer)
        advances with each read access. Once exhausted, the code can be
        'rewound' using the :meth:`rewind` method.

        This property is an alias for the
        :attr:`badsnakes.libs.parser.Parser.code` property.

        Returns:
            io.StringIO: The textual code as an ``io.StringIO`` object.

        """
        return self._parser.code

    @property
    def name(self) -> str:
        """Public accessor to the current Python module's filename."""
        return self._name

    @property
    def name_and_parent(self) -> str:
        """Public accessor to the module's filename and parent directory.

        The logger and reporter use this property to display the module
        name and its parent directory, as this aids in clarity if a
        module name is used multiple times.

        """
        return os.path.join(os.path.basename(os.path.dirname(self._path)), self._name)

    @property
    def nodeclasses(self):
        """Public accessor to the AST node classes.

        Use this property to access the analyser(s) and results.

        """
        return self._nc

    @property
    def path(self) -> str:
        """Public accessor to the current Python module's path."""
        return self._path

    def analyse(self):
        """Call the ``analyse`` method for all of the node classes.

        A module is only analysed if 1) the module's AST could be parsed
        and 2) if the ``ast.body`` list has more than 1 element.

        Once the analysis is complete, the module classification is set.
        The classification can be accessed through the
        :attr:`classification` property.

        """
        # Bypass analysis if the module AST could not be parsed.
        # Or, if the body list only has 1 element. The user will have been
        # warned by the parser if there was a parsing issue.
        if len(getattr(self.ast_, 'body', [])) > 1:
            for nc in self._nc:
                nc.analyse()
            self._set_classification()
        else:
            logging.info('Likely not a Python code module, only 1 body element: %s', self._path)

    def display(self):
        """Display the attributes extracted from the abstract syntax tree.

        Generally, this is used as a debugging mechanism and not used for
        production-based reporting.

        This method is an alias for the
        :meth:`badsnakes.libs.extractor.Extractor.display` method.

        """
        self._extractor.display(name=self._name)

    def display_syntax_tree(self):
        """Display the syntax tree, as provided by ``ast``.

        Generally, this is used as a debugging mechanism and not used for
        production-based reporting.

        This method is an alias for the
        :meth:`badsnakes.libs.parser.Parser.display_syntax_tree` method.

        """
        self._parser.display_syntax_tree()

    def rewind(self):
        """Rewind the :attr:`code` text stream to be beginning.

        This method is an alias for the
        :meth:`badsnakes.libs.parser.Parser.rewind` method.

        """
        self._parser.rewind()

    def _build(self):
        """Build the node classes object for this module.

        When this method is called, the extracted attributes from each
        AST node are stored into the ``.items`` attribute of the
        respective :attr:`nodeclasses` node subclass. Each subclass'
        ``.items`` attribute will contain a list of
        :mod:`badsnakes.libs.containers` objects with the extracted
        attributes for analysis.

        Additionally, the attribute values for each node class are
        converted to lower case, for robust string matching.

        Node classes which are added:

            - Argument
            - Assignment
            - Attribute
            - Call
            - Constant
            - FunctionDef
            - Import (and ImportFrom)
            - CodeText

        """
        # pylint: disable=protected-access
        self._nc.arguments.items = self._extractor._args
        self._nc.assignments.items = self._extractor._assigns
        self._nc.attributes.items = self._extractor._attrs
        self._nc.calls.items = self._extractor._calls
        self._nc.constants.items = self._extractor._constants
        self._nc.functiondefs.items = self._extractor._funcdefs
        self._nc.imports.items = self._extractor._imports
        self._nc.codetext.items = []        # CodeText items are set after analysis.
        self._nc.codetext.module = self     # CodeText analyser needs the module.
        self._nc.tolower()

    def _extract(self):
        """Extract and store relevant attributes from a parsed AST."""
        self._extractor.extract(node=self._parser.ast_)

    def _init(self):
        """Initialiser for this :class:`Module` class' instance.

        On initialisation, the following methods are called once the
        module's filepath and filename have been set:

            - :meth:`_parse`
            - :meth:`_extract`
            - :meth:`_build`

        """
        self._path = os.path.realpath(self._path)
        self._name = os.path.basename(self._path)
        self._parse()
        self._extract()
        self._build()

    def _parse(self):
        """Parse a Python module into an abstract syntax tree."""
        self._parser.parse(path=self._path)

    def _set_classification(self):
        """Set the severity classification for the module.

        Note:
            A ``filter`` is used to remove any empty ``.items`` lists.

        """
        # This is required, the linter is wrong.
        # pylint: disable=nested-min-max
        self._clf = max(max(filter(lambda x: x.items, self._nc))).severity


# %% Related private class implementations.

class _NodeClasses:
    """An iterable class which contains the AST node classes.

    Each of the subclasses contains an :attr:`items` and :attr:`_analyser`
    attribute. The ``.items`` attribute contains the AST node classes
    which were parsed from the source code. The ``._analyser`` attribute
    holds the node-specific analyser class which contains a ``.analyse``
    function to carry out the analysis.

    """

    __slots__ = (
                 'arguments',
                 'assignments',
                 'attributes',
                 'calls',
                 'codetext',
                 'constants',
                 'functiondefs',
                 'imports',
                )

    def __init__(self):
        """_NodeClasses class initialiser."""
        self.arguments = _NodeArguments()
        self.assignments = _NodeAssignments()
        self.attributes = _NodeAttributes()
        self.calls = _NodeCalls()
        self.codetext = _CodeText()
        self.constants = _NodeConstants()
        self.functiondefs = _NodeFunctionDefs()
        self.imports = _NodeImports()

    def __iter__(self):
        """Enable iteration through the defined node classes.

        This iterator returns (yields) the embedded *instance* for each
        AST node class.

        """
        for attr in self.__slots__:
            yield getattr(self, attr)

    def tolower(self):
        """Convert specific container attributes to lower case.

        When container attributes are in lower case, this enables more
        robust string searches, and enables the ``config.toml`` file to
        contain only lower case strings, rather than several variations.

        The method containing the actual implementation is
        :meth:`badsnakes.libs.containers._NodeBase.tolower`. This method
        is a simple wrapper to call this function on each node class.

        """
        for nc in self:
            for i in nc.items:
                i.tolower()


class _NodeBase:
    """Base class for all specialised AST node classes.

    These classes contain an :attr:`items` attribute which is a list
    holding the AST extraction containers for analysis, and the
    specialised AST node class analyser.

    The implementation for the analysers can be found in the
    :mod:`analysers` module.

    """

    def __init__(self):
        """Node base class initialiser."""
        self.items = None
        self.name = None
        self._analyser = None

    def __gt__(self, other):
        """Greater than operator implementation.

        This method enables the comparison of node classes, based on the
        ``severity`` attribute.

        """
        if all((self.items, other.items)):
            return max(self) > max(other)
        return False

    def __iter__(self):
        """Enable iteration through a node class' items."""
        yield from self.items

    def __lt__(self, other):
        """Less than operator implementation.

        This method enables the comparison of node classes, based on the
        ``severity`` attribute.

        """
        if all((self.items, other.items)):
            return min(self) < min(other)
        return False

    @property
    def analyser(self):
        """Public accessor to the node class' analyser class."""
        return self._analyser

    def analyse(self):
        """Callable for running the analyser for the specific node class.

        The :attr:`items` attribute containing a list of AST node
        container objects is passed into the node-class-specific
        analyser by this method call.

        """
        self._analyser.analyse(nodes=self.items)


class _CodeText(_NodeBase):
    """Specialised class for textual code analysis."""

    def __init__(self):
        """Code class initialiser."""
        super().__init__()
        self.name = 'codetext'
        self.module = None  # The module.Module object for analysis.
        self._analyser = CodeTextAnalyser()

    def analyse(self):
        """Callable for running the analyser for the code text.

        The :attr:`items` attribute containing a list of AST node
        container objects is passed into the node-class-specific
        analyser by this method call.

        """
        self._analyser.analyse(module=self.module)


class _NodeArguments(_NodeBase):
    """Specialised node class for AST Argument nodes."""

    def __init__(self):
        """Argument node class initialiser."""
        super().__init__()
        self.name = 'arguments'
        self._analyser = ArgumentAnalyser()


class _NodeAssignments(_NodeBase):
    """Specialised node class for AST Assignment nodes."""

    def __init__(self):
        """Assignment node class initialiser."""
        super().__init__()
        self.name = 'assignments'
        self._analyser = AssignmentAnalyser()


class _NodeAttributes(_NodeBase):
    """Specialised node class for AST Attribute nodes."""

    def __init__(self):
        """Attribute node class initialiser."""
        super().__init__()
        self.name = 'attributes'
        self._analyser = AttributeAnalyser()


class _NodeCalls(_NodeBase):
    """Specialised node class for AST Call nodes."""

    def __init__(self):
        """Call node class initialiser."""
        super().__init__()
        self.name = 'calls'
        self._analyser = CallAnalyser()


class _NodeConstants(_NodeBase):
    """Specialised node class for AST Constant nodes."""

    def __init__(self):
        """Constant node class initialiser."""
        super().__init__()
        self.name = 'constants'
        self._analyser = ConstantAnalyser()


class _NodeFunctionDefs(_NodeBase):
    """Specialised node class for AST FunctionDef nodes."""

    def __init__(self):
        """Constant node class initialiser."""
        super().__init__()
        self.name = 'functiondefs'
        self._analyser = FunctionDefAnalyser()


class _NodeImports(_NodeBase):
    """Specialised node class for AST Import and ImportFrom nodes."""

    def __init__(self):
        """Constant node class initialiser."""
        super().__init__()
        self.name = 'imports'
        self._analyser = ImportAnalyser()
