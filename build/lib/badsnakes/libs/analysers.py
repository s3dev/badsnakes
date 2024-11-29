#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the AST node analysers for the project.

            The analyser classes in this module iterate over the
            AST-node-specific :mod:`badsnakes.libs.containers` objects
            which store the details extracted from each AST node. Using
            the values defined in ``config.toml`` the ``severity`` flag
            in each container object is set according to the severity of
            the node analysis.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""
# pylint: disable=import-error
# pylint: disable=no-member  # Cannot add '_key' to base.

# Enable type hinting
from __future__ import annotations

import copy
import logging
import re
# locals
from badsnakes.libs.enums import Severity
from badsnakes.libs.config import analysercfg
from badsnakes.libs.containers import CodeText

logger = logging.getLogger(__name__)


class _BaseAnalyser:
    """Base analyser class.

    This class contains base functionality which is designed to be
    inherited and specialised as required by the node-type-specific
    classes.

    """

    def __init__(self):
        """Base code analyser class initialiser."""
        self._d = []            # Dangerous items.
        self._d_lstr = []       # Dangerous long strings.
        self._s = []            # Suspect items.
        self._s_lstr = []       # Suspect long strings.
        self._nodes = None      # AST node extractions to be analysed.
        self._cfg = analysercfg.get(self._key)   # Set the node-specific config.
        if self._cfg:
            self._kwds_d = set(self._cfg['dangerous'].get('kwds'))  # Set node-specific keywords.
            self._kwds_o = set(self._cfg['ok'].get('kwds'))         # Set node-specific keywords.
            self._kwds_s = set(self._cfg['suspect'].get('kwds'))    # Set node-specific keywords.

    @property
    def dangerous(self) -> list:
        """Public accessor to the AST nodes flagged as *dangerous*."""
        return self._d

    @property
    def dangerous_longstring(self) -> list:
        """Public accessor to long strings flagged as *dangerous*."""
        return self._d_lstr

    @property
    def suspect(self) -> list:
        """Public accessor to the AST nodes flagged as *suspect*."""
        return self._s

    @property
    def suspect_longstring(self) -> list:
        """Public accessor to long strings flagged as *suspect*."""
        return self._s_lstr

    def analyse(self, nodes: list):
        """Run the analyser against this module.

        For most AST nodes, the analyser first performs a 'quick search'
        to determine if any of the listed keywords from the config file
        are found in the AST extraction. If no keywords are present, no
        further analysis is performed. If keywords are present, the
        extracted statements are analysed further and flagged
        accordingly.

        Args:
            nodes (list): A list of :mod:`badsnakes.libs.containers`
                objects containing the values extracted from the AST
                nodes.

        :Implementation note:
            The call to :meth:`_suspect` must be made *before* the call
            to :meth:`_dangerous`.

            There is a check in some :meth:`_dangerous` methods which
            test if the AST node has already been flagged as 'suspect'.
            If so, a copy of the node class container is made so as not
            to re-classify suspect statements as dangerous; a copy of the
            container will be classified as dangerous. Obviously, this
            will result is double-reporting, but that's OK.

        """
        if nodes:
            self._nodes = nodes
            self._quick_search()
            self._suspect()  # Must be called *before* _dangerous.
            self._dangerous()

    def _dangerous(self):
        """Search for dangerous code elements for this node type.

        Any statements flagged as dangerous are written to the
        :attr:`_d` attribute.

        Note:
            This is a *generalised* dangerous search method which looks
            at the ``node.value`` attribute only.

        """
        results = []
        if self._cfg['dangerous']['long_strings']:
            self._d_lstr = self._find_long_strings(items=self._nodes,
                                                   category=Severity.DANGEROUS)
        if self._d:
            for n in self._nodes:
                if n in self._s:  # If already SUSPECT, do not overwrite.
                    n = copy.copy(n)
                if n.value in self._d:
                    n.severity = Severity.DANGEROUS
                    results.append(n)
        else:
            self._no_dangerous_items_found()
        self._d = results

    def _find_long_strings(self,
                           items: list,
                           category: Severity=Severity.SUSPECT) -> list:
        """Search for long strings in the node values.

        Args:
            items (list): A list of :mod:`badsnakes.libs.containers`
                objects containing the node classes to be analysed.
            category (Severity, optional): The
                :class:`~badsnakes.libs.enums.Severity` class enum to be
                assigned to flagged strings.
                Defaults to ``Severity.SUSPECT``.

        Returns:
            list: A list of badsnakes container objects containing long
            string values.

        """
        results = []
        for i in items:
            if (isinstance(i.value, (str, bytes))
                and len(i.value) > analysercfg['max_string_length']):
                i.severity = category
                results.append(i)
        return results

    def _no_dangerous_items_found(self):
        """Report that no dangerous items were found in the quick search."""
        logger.debug('%s: No dangerous items found in quick search. Not analysing.',
                     self._key.title())

    def _no_suspect_items_found(self):
        """Report that no suspect items were found in the quick search."""
        logger.debug('%s: No suspect items found in quick search. Not analysing.',
                     self._key.title())

    def _quick_search(self):
        """Search through extracted attributes for blacklisted items.

        A set of blacklisted items for this node type is compared against
        a set of extracted attributes for this node type. Further analysis
        is only carried out if there is an intersection in the two sets.

        Note:
            This is a *generalised* quick search method which looks at
            the ``node.value`` attribute only.

        """
        found = set()
        for n in self._nodes:
            found.add(n.value)
        self._s = (found & self._kwds_s) - self._kwds_o  # Subtract whitelist
        self._d = (found & self._kwds_d) - self._kwds_o  # Subtract whitelist

    def _suspect(self):
        """Search for suspect code elements for this node type.

        Any statements flagged as suspect are written to the
        :attr:`_s` attribute.

        Note:
            This is a *generalised* dangerous search method which looks
            at the ``node.value`` attribute only.

        """
        results = []
        if self._cfg['suspect']['long_strings']:
            self._s_lstr = self._find_long_strings(items=self._nodes)
        if self._s:
            for n in self._nodes:
                if n.value in self._s:
                    n.severity = Severity.SUSPECT
                    results.append(n)
        else:
            self._no_suspect_items_found()
        self._s = results


# %% Specialised analyser classes

class ArgumentAnalyser(_BaseAnalyser):
    """Specialised analyser class for the *Argument* node class."""

    def __init__(self):
        self._key = 'argument'
        super().__init__()


class AssignmentAnalyser(_BaseAnalyser):
    """Specialised analyser class for the *Assignment* node class."""

    def __init__(self):
        self._key = 'assignment'
        super().__init__()


class AttributeAnalyser(_BaseAnalyser):
    """Specialised analyser class for the *Attribute* node class."""

    def __init__(self):
        self._key = 'attribute'
        super().__init__()

    def _dangerous(self):
        """Search for dangerous code elements for this node type.

        Any statements flagged as dangerous are written to the
        :attr:`_d` attribute.

        Note:
            This method is specific to the node type, which looks at
            the ``node.name`` and ``node.value`` attributes.

        """
        results = []
        if self._d:
            for n in self._nodes:
                if n in self._s:  # If already SUSPECT, do not overwrite.
                    n = copy.copy(n)
                if f'{n.name}.{n.value}' in self._d:
                    n.severity = Severity.DANGEROUS
                    results.append(n)
        else:
            self._no_dangerous_items_found()
        self._d = results

    def _quick_search(self):
        """Search through extracted attributes for blacklisted items.

        A set of blacklisted items for this node type is compared against
        a set of extracted attributes for this node type. Further analysis
        is only carried out if there is an intersection in the two sets.

        Note:
            This method is specific to the node type, which looks at
            the ``node.name`` and ``node.value`` attributes.

        """
        found = set()
        for n in self._nodes:
            found.add(f'{n.name}.{n.value}')
        self._s = found & self._kwds_s
        self._d = found & self._kwds_d

    def _suspect(self):
        """Search for suspect code elements for this node type.

        Any statements flagged as suspect are written to the
        :attr:`_s` attribute.

        Note:
            This method is specific to the node type, which looks at
            the ``node.name`` and ``node.value`` attributes.

        """
        results = []
        if self._s:
            for n in self._nodes:
                if f'{n.name}.{n.value}' in self._s:
                    n.severity = Severity.SUSPECT
                    results.append(n)
        else:
            self._no_suspect_items_found()
        self._s = results


class CallAnalyser(_BaseAnalyser):
    """Specialised analyser class for the *Call* node class."""

    def __init__(self):
        self._key = 'call'
        super().__init__()

    def _dangerous(self):
        """Search for dangerous code elements for this node type.

        Any statements flagged as dangerous (which are not in the
        whitelist) are written to the :attr:`_d` attribute.

        Note:
            This method is specific to the node type, which looks at
            the ``node.name`` and ``[node.module].[node.name]``
            attributes.

        """
        results = []
        if self._d:
            for n in self._nodes:
                if n in self._s:  # If already SUSPECT, do not overwrite.
                    n = copy.copy(n)
                if ((n.name in self._d or f'{n.module}.{n.name}' in self._d)
                    and f'{n.module}.{n.name}' not in self._kwds_o):
                    n.severity = Severity.DANGEROUS
                    results.append(n)
        else:
            self._no_dangerous_items_found()
        self._d = results

    def _quick_search(self):
        """Search through extracted attributes for blacklisted items.

        A set of blacklisted items for this node type is compared against
        a set of extracted attributes for this node type. Further analysis
        is only carried out if there is an intersection in the two sets.

        Note:
            This method is specific to the node type, which looks at
            the ``node.name`` and (``node.module`` and ``node.name``)
            attributes.

        """
        found = set()
        for n in self._nodes:
            found.add(n.name)
            found.add(f'{n.module}.{n.name}')
        self._s = found & self._kwds_s
        self._d = found & self._kwds_d

    def _suspect(self):
        """Search for suspect code elements for this node type.

        Any statements flagged as suspect are written to the
        :attr:`_s` attribute.

        Note:
            This method is specific to the node type, which looks at
            the ``node.module`` and ``node.name`` attributes.

            Both the [.function] name and the [module.function] are
            tested. Additionally, if a function name is only a single
            character in length, it is flagged.

        """
        results = []
        if self._s:
            for n in self._nodes:
                if (n.name in self._s
                    or f'{n.module}.{n.name}' in self._s
                    # _ is reserved for the DANGEROUS category although 1 char in length.
                    or (len(n.name) == 1 and n.name != '_')):
                    n.severity = Severity.SUSPECT
                    results.append(n)
        else:
            self._no_suspect_items_found()
        self._s = results


class CodeTextAnalyser(_BaseAnalyser):
    """Analyse the textual code itself for suspect activity.

    This analyser class is different from the other analysers in this
    module as the checks performed are based on the textual code base,
    rather than on parsed AST node extractions.

    :Checks:
        The checks performed by this class are:

            - Modules with no defined functions or imports.
            - High percentage of long lines, relative to the number of
              lines in a module.
            - A high percentage of semi-colons, relative to the number of
              lines in a module.

        As these techniques are often used by threat actors to obfuscate
        code, these checks should pass for well-written / PEP oriented
        Python code, and are expected to trigger for suspect or poorly
        written code.

    """
    # The analyse method uses 'module' rather than 'nodes'. Done for clarity.
    # pylint: disable=arguments-renamed
    def __init__(self):
        self._key = 'code'
        super().__init__()
        self._nlines = 0
        self._m = None

    def analyse(self, module: Module):  # noqa # pylint: disable=undefined-variable
        """Run the code text analyser against this module.

        Args:
            module (module.Module): A :class:`~badsnakes.libs.module.Module`
                class containing the stream of textual code to be
                analysed, and ``module.nodeclasses`` object for further
                inspection.

        :Code analysis:

            - Suspect:

                - Single line modules
                - Modules with no defined functions or imports
                - Modules with a high percentage of long lines

            - Dangerous:

                - A 'frequent' use of semi-colons, relative to the
                  number of lines in the module

        """
        # Bypass analysis if the module AST could not be parsed. The user
        # will have been warned by the parser if there was an issue.
        if module.ast_:
            self._m = module
            self._get_line_count()
            self._test_high_pct_long_lines()
            self._test_high_pct_semi_colons()
            self._test_no_function_defs_no_imports()
            self._test_single_line_module()
            self._set_items()

    def _get_line_count(self):
        """Count the lines of *code* in the module.

        The number of lines is determined by traversing the top level of
        the AST and storing the ``node.lineno`` and ``node.end_lineno``
        attributes into a set (to prevent duplication), then summing
        the difference in last-first+1, to get the total number of
        *coded* lines in a module.

        This approach is used as this skips comments and blank lines and
        only accounts the actual lines of code.

        """
        # pylint: disable=protected-access
        lines = set()
        for n in self._m._parser.ast_.body:  # Only traverse the module's top-level.
            if hasattr(n, 'lineno'):
                lines.add((n.lineno, n.end_lineno))
        self._nlines = sum(l - f + 1 for f, l in lines)

    def _no_function_defs(self) -> bool:
        """Test if the code has no function definitions.

        Returns:
            bool: True if the
            :attr:`badsnakes.libs.module.Module._NodeFunctionDefs.items`
            list is empty, otherwise False.

        """
        return not self._m.nodeclasses.functiondefs.items

    def _no_imports(self) -> bool:
        """Test if the code has no imports.

        Returns:
            bool: True if the
            :attr:`badsnakes.libs.module.Module._NodeImports.items`
            list is empty, otherwise False.

        """
        return not self._m.nodeclasses.imports.items

    def _set_items(self):
        """Set the ``.items`` attribute with the results.

        Typically, the module object will set the items on build with
        container object populated by the extractor. However, as code
        text analysis operates differently, the items are set here using
        the containers populated on analysis.

        """
        self._m.nodeclasses.codetext.items.extend(self._s + self._d)

    def _test_high_pct_long_lines(self):
        """Test if the code has a high percentage of long lines.

        The maximum line length is defined in ``config.toml`` along with
        the percentage used by the test.

        :Logic:
            - Rewind the code stream to the beginning.
            - Create a filter object containing lines whose length is
              greater than the maximum allowed, and obtain the length
              of the result.
            - Divide the result by the number of lines in the module and
              test if the ratio is greater than or equal to the allowed
              limit.
            - If the result of the test is True, a
              :class:`badsnakes.libs.containers.CodeText` container is
              appended to the :attr:`_s` suspect attribute with the
              relevant details.

        Note:
            For an overview of how a module's lines are counted, refer
            to the docstring for the :meth:`_get_line_count` method.

        """
        # pylint: disable=line-too-long  # N: 101
        # pylint: disable=unnecessary-comprehension  # More compact
        self._m.rewind()
        n = len([_ for _ in filter(lambda x: len(x) > analysercfg['max_line_length'], self._m.code)])
        if (n / self._nlines) >= analysercfg['pct_long_lines']:
            self._s.append(CodeText(reason='High percentage of long lines.',
                                    severity=Severity.SUSPECT))

    def _test_high_pct_semi_colons(self):
        """Test for the use of semi-colons relative to line count.

        This test is designed to detect semi-colons which are used as
        *statement separators* in the code itself, as the
        :class:`ConstantAnalyser` class detects
        semi-colons in strings.

        The percentage of semi-colons relative to the number of lines is
        defined in the ``config.toml`` file.

        :Logic:
            - Rewind the code stream to the beginning.
            - Iterate through the code stream and count the number of
              semi-colons on each line, and sum the results.
            - Divide the summed result by the number of lines in the
              module and test if the ratio is greater than or equal to
              the allowed limit.
            - If the result of the test is True, a
              :class:`badsnakes.libs.containers.CodeText` container is
              appended to the :attr:`_d` dangerous attribute with the
              relevant details.

        Note:
            For an overview of how a module's lines are counted, refer
            to the docstring for the :meth:`_get_line_count` method.

        """
        self._m.rewind()
        c = sum(i.count(';') for i in self._m.code)
        if (c / self._nlines) >= analysercfg['pct_semi_colons']:
            self._d.append(CodeText(reason='High percentage of semi-colons.',
                                    severity=Severity.DANGEROUS))

    def _test_no_function_defs_no_imports(self):
        """Test if the code has no function definitions or imports.

        :Logic:
            - Test if a call to the :meth:`_no_function_defs` and
              :meth:`_no_imports` methods are True.
            - If True, a :class:`badsnakes.libs.containers.CodeText`
              container is appended to the :attr:`_s` suspect attribute
              with the relevant details.

        """
        if self._no_function_defs() and self._no_imports():
            self._s.append(CodeText(reason='No function definitions and no imports.',
                                    severity=Severity.SUSPECT))

    def _test_single_line_module(self):
        """Test if a module only contains a single line of code.

        Generally, this is an indication of a runner script, or a long
        statement (or string) used to obfuscate malicious code.

        :Logic:
            - If the :attr:`_nlines` attribute is less than two, a
              :class:`badsnakes.libs.containers.CodeText` container is
              appended to the :attr:`_s` suspect attribute with the
              relevant details.

        :Rationale:
            For rationale on how lines of code are counted, refer to the
            docstring for the :meth:`_get_line_count` method.

        """
        if self._nlines < 2:
            self._s.append(CodeText(value=self._nlines,
                                    reason='Single line module.',
                                    severity=Severity.SUSPECT))


class ConstantAnalyser(_BaseAnalyser):
    """Specialised analyser class for the *Constant* node class.

    Note:
        All function/method docstrings have been *excluded* from the
        containers enabling the search for simple strings such as
        ``';'`` and ``'()'`` in constants, without the presence of these
        strings in the docstring flagging a false-positive.

        The docstring extraction is performed by the
        :meth:`extractor._extract_docstrings` method.

    """

    #
    # Used to catch strings with () and no spaces. For example:
    # - '()'
    # - 'fn()'
    # - 'fn1();fn2()'
    #
    # But not:
    # - 'A string instructing user to call this fn() instead.'
    #
    _RE_PAREN = re.compile(r'^\S*\(\)\S*$')

    def __init__(self):
        self._key = 'constant'
        super().__init__()

    def _dangerous(self):
        """Search for dangerous code elements for this node type.

        Any statements flagged as dangerous are written to the
        :attr:`_d` attribute.

        Note:
            This method is specific to the node type, which looks at
            the ``node.value`` attribute.

            The constants tests do *not* rely on the quick search, as we
            are searching for blacklisted strings *in* constants
            (strings). Therefore, as each constant is iterated a full
            blacklist search is occurring.

            Granted, it's not efficient - but we must be thorough.

        """
        results = []
        for n in self._nodes:
            if n in self._s:  # If already SUSPECT, do not overwrite.
                n = copy.copy(n)
            # Test if the blacklisted string is any part of the constant.
            # This block is intentionally verbose (rather than using any())
            # so the search string can be added to the container.
            if n.value and isinstance(n.value, str):
                for d in self._kwds_d:
                    # Consider whitelisted strings.
                    # For example, exec in 'execution' string is OK.
                    if d in n.value and not any(d in ok for ok in self._kwds_o):
                        n.searchstr = d
                        n.severity = Severity.DANGEROUS
                        results.append(n)
                        break  # Only need to capture the first hit.
        self._d = results

    def _suspect(self):
        """Search for suspect code elements for this node type.

        Any statements flagged as suspect are written to the
        :attr:`_s` attribute.

        Note:
            This method is specific to the node type, which looks at
            the ``node.value`` attribute.

            The constants tests do *not* rely on the quick search, as we
            are searching for blacklisted strings *in* constants
            (strings). Therefore, as each constant is iterated a full
            blacklist search is occurring.

            Granted, it's not efficient - but we must be thorough.

        """
        results = []
        for n in self._nodes:
            # Test if the blacklisted string is any part of the constant.
            # This block is intentionally verbose (rather than using any())
            # so the search string can be added to the container.
            if n.value and isinstance(n.value, str):
                if self._RE_PAREN.search(n.value):
                    n.searchstr = self._RE_PAREN.pattern
                    n.severity = Severity.SUSPECT
                    results.append(n)
                else:
                    for s in self._kwds_s:
                        # Test if kwd is *any part* of the string.
                        if s in n.value:
                            n.searchstr = s
                            n.severity = Severity.SUSPECT
                            results.append(n)
                            break  # Only need to capture the first hit.
        self._s = results


class FunctionDefAnalyser(_BaseAnalyser):
    """Specialised analyser class for the *FunctionDef* node class."""

    def __init__(self):
        self._key = 'functiondef'
        super().__init__()

    def _dangerous(self):
        """Search for dangerous code elements for this node type.

        Any statements flagged as dangerous are written to the
        :attr:`_d` attribute.

        Note:
            This method is specific to the node type, which looks at
            the ``node.name`` attribute.

        """
        results = []
        if self._d:
            for n in self._nodes:
                if n in self._s:  # If already SUSPECT, do not overwrite.
                    n = copy.copy(n)
                if n.name in self._d:
                    n.severity = Severity.DANGEROUS
                    results.append(n)
        else:
            self._no_dangerous_items_found()
        self._d = results

    def _quick_search(self):
        """Search through extracted attributes for blacklisted items.

        A set of blacklisted items for this node type is compared against
        a set of extracted attributes for this node type. Further analysis
        is only carried out if there is an intersection in the two sets.

        Note:
            This method is specific to the node type, which looks at
            the ``node.name`` attribute.

        """
        found = set()
        for n in self._nodes:
            found.add(n.name)
        self._s = found & self._kwds_s
        self._d = found & self._kwds_d

    def _suspect(self):
        """Search for suspect code elements for this node type.

        Any statements flagged as suspect are written to the
        :attr:`_s` attribute.

        Note:
            This method is specific to the node type, which looks at
            the ``node.name`` attribute.

            As all function names are tested (specifically in search of
            single character function names) the quick search is
            bypassed.

            Additionally, any function names containing ``'0x'`` in the
            name are flagged as this suggests an attempt at obfuscation.

        """
        results = []
        for n in self._nodes:
            if (n.name in self._s
                or len(n.name) == 1
                or '0x' in n.name):
                n.severity = Severity.SUSPECT
                results.append(n)
        self._s = results


class ImportAnalyser(_BaseAnalyser):
    """Specialised analyser class for the *Import* node class."""

    def __init__(self):
        self._key = 'import'
        super().__init__()

    def _dangerous(self):
        """Search for dangerous code elements for this node type.

        Any statements flagged as dangerous are written to the
        :attr:`_d` attribute.

        Note:
            This method is specific to the node type, which looks at
            the ``node.module`` and (``node.module``.``node.name``)
            attributes.

        """
        results = []
        if self._d:
            for n in self._nodes:
                if n in self._s:  # If already SUSPECT, do not overwrite.
                    n = copy.copy(n)
                if n.module in self._d or f'{n.module}.{n.name}' in self._d:
                    n.severity = Severity.DANGEROUS
                    results.append(n)
        else:
            self._no_dangerous_items_found()
        self._d = results

    def _quick_search(self):
        """Search through extracted attributes for blacklisted items.

        A set of blacklisted items for this node type is compared against
        a set of extracted attributes for this node type. Further analysis
        is only carried out if there is an intersection in the two sets.

        Note:
            This method is specific to the node type, which looks at
            the ``node.module`` and (``node.module``.``node.name``)
            attributes.

        """
        found = set()
        for n in self._nodes:
            found.add(n.module)
            found.add(f'{n.module}.{n.name}')
        self._s = found & self._kwds_s
        self._d = found & self._kwds_d

    def _suspect(self):
        """Search for suspect code elements for this node type.

        Any statements flagged as suspect are written to the
        :attr:`_s` attribute.

        Note:
            This method is specific to the node type, which looks at
            the ``node.module`` and (``node.module``.``node.name``)
            attributes.

        """
        results = []
        if self._s:
            for n in self._nodes:
                if n.module in self._s or f'{n.module}.{n.name}' in self._s:
                    n.severity = Severity.SUSPECT
                    results.append(n)
        else:
            self._no_suspect_items_found()
        self._s = results
