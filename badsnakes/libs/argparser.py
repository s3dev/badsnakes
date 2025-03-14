#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides command line argument parsing
            functionality.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""
# pylint: disable=import-error
# pylint: disable=no-member  # ExCode does have the members.

import argparse
import logging
import os
import sys
# locals
from badsnakes.libs.config import config, projectcfg
from badsnakes.libs.enums import ExCode
from badsnakes.libs._version import __version__


class ArgParser:
    """Project command line argument parser."""

    # Program usage and help strings.
    _proj = projectcfg['name']
    _desc = projectcfg['desc']
    _vers = __version__
    _usag = 'badsnakes PATH [options] [--help]'
    _h_dbug = 'Display debugging output to the terminal.'
    _h_excl = 'Directories to be excluded from file collection.'
    _h_help = 'Display this help and usage, then exit.'
    _h_logg = ('Store the analysis results into a log file on your desktop,\n'
               'or the path provided to --logpath.')
    _h_logp = ('Path into which the log file(s) will be stored.\n'
               'Notes:\n'
               '- The path *must* already exist, otherwise the program will abort.\n'
               '- If not provided, the logs are stored to the user\'s desktop.')
    _h_path = ('Path(s) to the Python module(s) or wheel(s) to be analysed.\n'
               '- If files, glob wildcard patterns are honoured.\n'
               '  For example, *.py or *.whl.\n'
               '- If directories are provided, *all* non-binary files are\n'
               '  collected for analysis. Note, the --exclude_dirs argument\n'
               '  can be used to exclude specific directories.\n\n'
               'Note: All PATH(s) must be of the same type.\n')
    _h_verb = ('Display verbose analysis findings to the terminal.\n'
               '- By default, only the overall finding is displayed, per\n'
               '  module.')
    _h_vers = 'Display the version, then exit.'

    def __init__(self):
        """Project argument parser class initialiser."""
        self._args = None
        self._epil = self._build_epilog()
        self._excode = ExCode.OK.value

    @property
    def args(self):
        """Accessor to parsed arguments."""
        return self._args

    def parse(self):
        """Parse command line arguments."""
        # pylint: disable=line-too-long
        argp = argparse.ArgumentParser(prog=self._proj,
                                       usage=self._usag,
                                       description=self._desc,
                                       epilog=self._epil,
                                       formatter_class=argparse.RawTextHelpFormatter,
                                       add_help=False)
        # Order matters here as it affects the display -->
        argp.add_argument('PATH', help=self._h_path, nargs='+')
        argp.add_argument('-e', '--exclude_dirs', help=self._h_excl, nargs='+')
        argp.add_argument('-d', '--debug', help=self._h_dbug, action='store_true')
        argp.add_argument('-l', '--log', help=self._h_logg, action='store_true')
        argp.add_argument('-v', '--verbose', help=self._h_verb, action='store_true')
        argp.add_argument('-h', '--help', help=self._h_help, action='help')
        argp.add_argument('-V', '--version', help=self._h_vers, action='version', version=self._epil)
        argp.add_argument('--logpath', help=self._h_logp, nargs=1)
        self._args = argp.parse_args()
        self._set_logger()
        logging.debug('CLI arguments: %s', self._args)
        try:
            self._verify_args()
        except ValueError as err:
            argp.print_help()
            print('')
            logging.critical(err)
            print('')
            sys.exit(self._excode)

    def _build_epilog(self) -> str:
        """Build the epilog string for terminal display.

        Returns:
            str: A string containing the text to be displayed in the
            epilog of the help menu.

        """
        path = os.path.join(config.dir_root, 'NOTICE')
        with open(path, 'r', encoding='utf-8') as f:
            notice = f.read()
        epil = f'{notice}\n\n{self._proj} v{self._vers}'
        return epil

    def _set_logger(self):
        """Set the debugging level based on the CLI argument.

        The default logging level is set using the ``project.log_level``
        key in ``config.toml``. However, if the ``--debug`` argument is
        passed, the log level is set to 10 (DEBUG).

        :Levels:
            - 10: DEBUG
            - 20: INFO
            - 30: WARNING
            - 40: ERROR
            - 50: CRITICAL

        """
        level = 10 if self._args.debug else projectcfg['log_level']
        logging.basicConfig(level=level, format="[%(levelname)s]: %(message)s")

    def _verify_args(self):
        """Verify the provided arguments are valid.

        If any argument is not valid, a ``ValueError`` is raised and the
        appropriate exit code is set.

        """
        if self._args.logpath:
            self._args.logpath = self._args.logpath[0]
            if not os.path.exists(self._args.logpath):
                self._excode = ExCode.ERR_ARGP_LOGP.value
                raise ValueError(f'The requested log path does not exist: {self._args.logpath}')


# Make the arg parser accessible as an import.
argparser = ArgParser()
