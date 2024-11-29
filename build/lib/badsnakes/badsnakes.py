#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:App:       badsnakes
:Purpose:   The badsnakes project is designed to help detect malware in
            Python projects.

            The project accepts the following formats for analysis:

                - Directories
                - Python modules
                - Python wheels

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

:Examples:

    Example for analysing a single module::

        >>> from badsnakes.libs.module import Module
        >>> from badsnakes.libs.reporter import ReporterModule

        >>> path = '/path/to/project/module.py'

        >>> # Analyse the module.
        >>> m = Module(path=path)
        >>> m.analyse()

        >>> # Report the findings.
        >>> r = ReporterModule(modules=[m])
        >>> r.report()


    Example for analysing multiple modules::

        >>> import os
        >>> from glob import glob
        >>> from badsnakes.libs.module import Module
        >>> from badsnakes.libs.reporter import ReporterModule

        >>> modules = []
        >>> paths = glob(os.path.join('/.../site-packages/pip/_internal/', '*.py'))

        >>> # Call Module.analyse for each path and store each module object.
        >>> for path in paths:
        >>>    m = Module(path=path)
        >>>    m.analyse()
        >>>    modules.append(m)

        >>> # Report all findings at once.
        >>> r = ReporterModule(modules=modules)
        >>> r.report()


    Example for analysing a Python wheel::

        >>> from badsnakes.libs.collector import Collector
        >>> from badsnakes.libs.module import Module
        >>> from badsnakes.libs.reporter import ReporterModule

        >>> modules = []
        >>> path = '../dist/badsnakes-0.1.0-py3-none-any.whl'

        >>> # Collect all non-binary files from thw wheel.
        >>> c = Collector(paths=path)
        >>> c.collect()

        >>> for pkg in c.files:
        >>>    # Call Module.analyse for each path and store each module object.
        >>>    for path in pkg:
        >>>        # Analyse the module.
        >>>        m = Module(path=path)
        >>>        m.analyse()
        >>>        modules.append(m)

        >>> # Report the findings.
        >>> r = ReporterModule(modules=modules)
        >>> r.report()

"""
# pylint: disable=wrong-import-position

import os
import sys
# Update sys.path for project/relative imports.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
# imports
import logging
import traceback
from datetime import datetime as dt
# locals
from badsnakes.libs.argparser import argparser as ap
from badsnakes.libs.collector import Collector
from badsnakes.libs.containers import Severity
from badsnakes.libs.enums import ExCode
from badsnakes.libs.module import Module
from badsnakes.libs.reporter import ReporterModule
from badsnakes.libs.logger import Logger
from badsnakes.libs.utilities import utilities


class BadSnakes:
    """Primary project entry-point and controller class."""

    def __init__(self):
        """BadSnakes class initialiser.

        :Attrs:
            - _clf: Maximum classification from all files analysed. This
              is reported at the end.
            - _files: List of files to be analysed. This same list is
              used for all analysis types and is populated by the
              :meth:`_collect_files` method.
            - _modules: List of modules analysed. If logging is invoked,
              this list of modules is given to the logger.

        """
        self._clf = Severity.UNKNOWN    # Maximum classification for all files.
        self._files = None              # Files to be analysed.
        self._modules = []              # Collection of modules analysed.
        self._collector = None          # Keep the wheel collector's tmpdir alive.
        ap.parse()

    def main(self):
        """Start a badsnakes analysis.

        :Tasks:
            - Collect files to be analysed.
            - Analyse each collected file.
            - Report the overall (worst) classification.
            - Create a log file, if instructed by the CLI by the
              ``--log`` argument.

        """
        file = None
        try:
            self._collect_files()
            for pkg in self._files:
                for file in pkg:
                    self._analyse(path=file)
            self._report_worst_classification()
            self._create_log()
        # General project error handler.
        except Exception:  # pragma: nocover
            print()
            logging.critical('The following error occurred:\n\n%s\n'
                             'Current file: %s\n\n'
                             'Processing aborted.\n',
                             traceback.format_exc(),
                             file or None)  # In the event of an empty package.
            sys.exit(ExCode.ERR_MAIN.value)

    def _analyse(self, path: str):
        """Analyse the provided module file.

        Args:
            path (str): Full path to the file to be analysed.

        :Tasks:
            - Create a :class:`~badsnakes.libs.module.Module` object and
              analyse.
            - Report the findings (verbose/non-verbose).
            - Set the maximum (worst) classification.

        """
        logging.debug('Analysing file: %s', os.path.basename(path))
        m = Module(path=path)
        m.analyse()
        r = ReporterModule(modules=m)
        # if args.verbose:
        if ap.args.verbose:
            r.report()
        else:
            r.report_classification_only()
        self._clf = max(self._clf, m.classification)
        self._modules.append(m)

    def _collect_files(self):
        """Collect all files to be analysed.

        This method is used to populate the :attr:`_files` attribute,
        which contains the files to be analysed.

        :Logic:
            Create an instance of the
            :class:`badsnakes.libs.collector.Collector` class and call
            the :meth:`~badsnakes.libs.collector.Collector.collect`
            method.

            The Collector class is designed to 1) identify the input
            type, and 2) return the associated file(s).

            The list of files returned by the collector is assigned to
            the :attr:`_files` attribute.

            Finally, any paths listed by the ``--exclude_dirs`` argument
            are removed from the :attr:`_files` list.

        This method must store the collector into a class attribute to
        preserve the life of the wheel collector's temporary directory
        object.

        """
        # self._collector = Collector(paths=args.PATH)
        self._collector = Collector(paths=ap.args.PATH)
        self._collector.collect()
        self._files = self._collector.files
        self._exclude_directories()

    def _create_log(self):
        """Create a log file if instructed via the CLI.

        If the ``--log`` argument was passed to the CLI, this method will
        be triggered.

        """
        # if args.log:
        if ap.args.log:
            dtme = dt.now().strftime('%Y%m%dT%H%M%S')
            path = os.path.join(os.path.expanduser('~/Desktop/'), f'badsnakes_{dtme}.log')
            logger = Logger(path=path, modules=self._modules)
            logger.write()

    def _exclude_directories(self):
        """Remove any paths starting in an ``--exclude_dirs`` path."""
        # pylint: disable=consider-using-f-string
        # if args.exclude_dirs:
        if ap.args.exclude_dirs:
            files = []
            for pkg in self._files:
                # This is intentionally verbose to enable debug logging.
                # keep = utilities.exclude_dirs(source=pkg, exclude=args.exclude_dirs)
                keep = utilities.exclude_dirs(source=pkg, exclude=ap.args.exclude_dirs)
                files.append(keep)
                logging.debug('Files excluded:')
                logging.debug('%s', '\n\t '.join(map('- {}'.format, set(pkg) - set(keep))))
            self._files = files

    def _report_worst_classification(self):
        """Report the worst overall classification."""
        print(f'\nOverall (worst) classification: {self._clf.name}\n')


# %% Prevent from running on module import.

# Enable running as either a script (dev/debugging) or as an executable.
if __name__ == '__main__':  # pragma: nocover
    bs = BadSnakes()
    bs.main()
else:  # pragma: nocover
    def main():
        """Entry-point exposed for the executable.

        The ``"badsnakes.badsnakes:main"`` value is set in
        ``pyproject.toml``'s ``[project.scripts]`` table as the
        entry-point for the installed executable.

        """
        # pylint: disable=redefined-outer-name
        bs = BadSnakes()
        bs.main()
