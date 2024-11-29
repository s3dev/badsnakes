#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the *terminal-based* reporting
            functionality for the project. File-based reporting is
            handled by the :mod:`badsnakes.libs.logger` module.

            There is a specific reporting class, based on the analysis
            provided:

                - :class:`ReporterModule`
                - :class:`ReporterPickle`
                - :class:`ReporterWheel`

            All of these classes inherit their base functionality from
            the private :class:`_ReporterBase` class.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  This module's implementation is very simple in that it only
            iterates a module's node classes and calls the ``.report()``
            method on each container, which provides the *formatting*
            for each message. The formatting is *not* controlled by this
            module.

            For example:

                - :meth:`badsnakes.libs.containers.Assign.report`
                - :meth:`badsnakes.libs.containers.Attribute.report`
                - :meth:`badsnakes.libs.containers.Call.report`
                - etc.

"""

# Enable type hinting
from __future__ import annotations


class _ReporterBase:
    """Currently not implemented."""


class ReporterModule(_ReporterBase):
    """Iterate all modules and report the findings for each node type.

    Args:
        modules (list[module.Module] | tuple[module.Module]): A list
            (or tuple) of :class:`badsnakes.libs.module.Module` objects
            containing the findings to be reported.

    """

    def __init__(self, modules: list[module.Module] | tuple[module.Module]):  # noqa # pylint: disable=undefined-variable
        """Base reporter initialiser class."""
        self._mods = modules if isinstance(modules, (list, tuple)) else [modules]
        self._m = None  # Module currently being reported.

    def report(self):
        """Primary reporting callable.

        This method iterates the modules provided on instantiation of the
        :class:`ReporterModule` class, and reports the
        node-class-specific findings for each.

        """
        for m in self._mods:
            self._m = m
            self._display_title()
            self._report_suspect()
            self._report_dangerous()
            self._report_classification()

    def report_classification_only(self):
        """Reporting callable for displaying the *classification only*.

        This method iterates the modules provided on instantiation of the
        :class:`ReporterModule` class, and reports each module's
        classification.

        """
        for m in self._mods:
            self._m = m
            self._report_classification_only()

    def _display_title(self):
        """Display a formatted version of the current module's name."""
        title = f' Module: {self._m.name_and_parent} '
        sep = '-' * len(title)
        print('', sep, title, sep, sep='\n')

    def _report_classification(self):
        """Report the current module's overall classification."""
        print('\nModule classification:', self._m.classification.name)

    def _report_classification_only(self):
        """Report the current module's overall classification.

        This method differs from the :meth:`_report_classification` in
        that this method also displays the module name, as the
        :meth:`report_classification_only` method does not print the
        module name in a title banner.

        """
        print(f'Module: {self._m.name_and_parent}, Classification: {self._m.classification.name}')

    def _report_dangerous(self):
        """For each node class, report the *dangerous* findings."""
        for nc in self._m.nodeclasses:
            for i in nc.analyser.dangerous:
                i.report()
            for i in nc.analyser.dangerous_longstring:
                i.report_longstring()

    def _report_suspect(self):
        """For each node class, report the *suspect* findings."""
        for nc in self._m.nodeclasses:
            for i in nc.analyser.suspect:
                i.report()
            for i in nc.analyser.suspect_longstring:
                i.report_longstring()


class ReporterPickle(_ReporterBase):
    """Report findings for a given pickle file.

    Raises:
        NotImplementedError: Currently not implemented. Available for
            future development.

    """

    def __init__(self):
        """Pickle analysis reporter class initialiser."""
        raise NotImplementedError('Pickle analysis is not implemented (yet).')


class ReporterWheel(_ReporterBase):
    """Report findings for all plaintext files in a given wheel.

    Raises:
        NotImplementedError: Currently not implemented. Available for
            future development.

    """

    def __init__(self):
        """Wheel analysis reporter class initialiser."""
        raise NotImplementedError('Wheel analysis is not implemented (yet).')
