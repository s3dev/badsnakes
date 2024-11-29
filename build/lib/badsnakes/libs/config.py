#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the functionality for reading and
            importing the ``config.toml`` file to the project.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  If the version of Python is 3.11+, the ``tomllib`` builtin
            is used to load the config file. Otherwise, the third-party
            ``toml`` library is used. If ``toml`` is not installed, the
            user is notified the library must be installed, and the
            program is exited.

:Example:
    Example code use::

        >>> from badsnakes.libs.config import (analysercfg,
                                               config,
                                               systemcfg)

"""
# pylint: disable=import-error

import logging
import os
import sys
# locals
from badsnakes.libs.enums import ExCode

logger = logging.getLogger(__name__)

# Check Python version. The tomllib is only available for >= 3.11.
_GEQ311 = sys.version_info >= (3, 11)
if _GEQ311:
    import tomllib
else:
    try:
        import toml
    except ImportError:
        msg = ('As a Python version less than 3.11 is being used, '
               'the toml library must be installed.')
        logger.critical(msg)
        sys.exit(ExCode.ERR_TOML.value)


class Config:
    """General project configuration wrapper class.

    Note:
        This class is used to simply read and provide access to the
        settings defined in the ``config.toml`` file.

        All configuration keys are to be set in the ``config.toml`` file,
        not in this module.

    """

    _DIR_ROOT = os.path.dirname(os.path.realpath(__file__))

    def __init__(self):
        """Configuration class initialiser."""
        self._alzcfg = None
        self._gencfg = None
        self._procfg = None
        self._syscfg = None
        self._load_config()

    @property
    def analyserconfig(self):
        """Public accessor to the analyser's configuration items."""
        return self._alzcfg

    @property
    def config(self):
        """Public accessor to all configuration items."""
        return self._gencfg

    @property
    def dir_root(self):
        """Public accessor to the project's root directory."""
        return self._DIR_ROOT

    @property
    def projectconfig(self):
        """Public accessor to project configuration items."""
        return self._procfg

    @property
    def systemconfig(self):
        """Public accessor to system configuration items."""
        return self._syscfg

    def _load_config(self):
        """Load the config TOML file into memory.

        This method is called on class instantiation.

        If using Python 3.11+, the builtin ``tomllib`` library is used
        to read the config file. Otherwise, the third-party ``toml``
        library is used.

        """
        path = os.path.join(self._DIR_ROOT, 'config.toml')
        if _GEQ311:
            with open(path, 'rb') as f:
                self._gencfg = tomllib.load(f)
        else:
            self._gencfg = toml.load(path)
        self._alzcfg = self._gencfg.get('analyser')
        self._procfg = self._gencfg.get('project')
        self._syscfg = self._gencfg.get('system')


config = Config()
analysercfg = config.analyserconfig
projectcfg = config.projectconfig
systemcfg = config.systemconfig
