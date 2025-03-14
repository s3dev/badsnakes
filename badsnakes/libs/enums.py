#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the various enumerators to the project.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

:Example:
            Import the ``Severity`` enumerator into a module::

                >>> from badsnakes.libs.enums import Severity

"""

import enum


class ExCode(enum.IntEnum):
    """Exit code enumerator class."""

    # No error
    OK = 0

    # Main (1-9)
    ERR_MAIN = 1   # Error from the BadSnakes.main, the main error handler.

    # Config module (20-29)
    ERR_TOML = 21  # The toml module is not installed (< 3.11).

    # Argparser (30-39)
    ERR_ARGP_LOGP = 30  # The requested log path does not exist.


class Severity(enum.IntEnum):
    """Statement severity enumerator class."""

    UNKNOWN = -1
    OK = 0
    SUSPECT = 1
    DANGEROUS = 2
