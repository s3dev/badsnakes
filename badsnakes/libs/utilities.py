#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides general utility-based functions to the
            project.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

:Examples:

    Test if a file is *binary*::

        >>> from badsnakes.libs.utilities import utilities

        >>> utilities.isbinary(path='/path/to/myfile.ext')
        True

    Test if a file is *text*::

        >>> from badsnakes.libs.utilities import utilities

        >>> utilities.istext(path='/path/to/myfile.py')
        True


    Test if a file is a *Python wheel*::

        >>> from badsnakes.libs.utilities import utilities

        >>> utilities.iszip(path='/path/to/mypackage.whl')
        True

"""

import os
from datetime import datetime as dt
# locals
from badsnakes.libs.argparser import argparser as ap


class Utilities:
    """Generalised utilities for use throughout the project."""

    __slots__ = ()
    _TEXTCHARS = set({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
    _ZIPSIG = b'\x50\x4b\x03\x04'
    _ZIPSIG_EMPTY = b'\x50\x4b\x05\x06'
    _ZIPSIG_SPAN = b'\x50\x4b\x07\x08'

    @staticmethod
    def derive_log_filename(path: str='badsnakes') -> str:
        """Derive the log filename from the provided path.

        Args:
            path (str, optional): Path from which the log filename is to
                be derived. If not provided, the default log base
                filename is used. Defaults to 'badsnakes'.

        :Logic:
            If ``path`` is provided, the basename is extracted and the
            file extension is dropped and any trailing '/' are dropped.
            This is used as the base for the filename convention.
            Otherwise, 'badsnakes' is used as the base.

            Filename convention::

                <base>__YmdTHMS.bs.log

            Additionally, if the ``--logpath`` argument was passed to the
            CLI, this directory is used. Otherwise the user's desktop is
            used as the directory.

        Returns:
            str: The complete path to the log file.

        """
        dir_ = ap.args.logpath if ap.args.logpath else os.path.expanduser('~/Desktop/')
        dtme = dt.now().strftime('%Y%m%dT%H%M%S')
        base = os.path.splitext(os.path.basename(path.strip('/')))[0]
        base = f'{base}__{dtme}.log'
        fpath = os.path.join(dir_, base)
        return fpath

    @staticmethod
    def exclude_dirs(source: list[str], exclude: list[str]) -> list[str]:
        """Exclude the listed directories from the source.

        Args:
            source (list[str]): List of source paths.
            exclude (list[str]): List of directories to be excluded from
                ``source``.

        :Design:
            The paths in ``exclude`` are expanded to their realpath, with
            a trailing path separator explicitly added to ensure only
            directory paths are matched.

            For example, if the trailing path separator was not added,
            ``.gitignore`` would be excluded if ``./.git`` was in
            ``exclude`` paths. Adding the trailing path separator
            prevents this.

        Returns:
            list[str]: A new list of paths where any ``source`` path
            sharing a common base path with any ``exclude`` path has
            been removed.

        """
        exclude = list(map(lambda x: f'{os.path.realpath(x)}/', exclude))
        return [s for s in source if all(e not in s for e in exclude)]

    @classmethod
    def isbinary(cls, path: str, size: int=1024) -> bool:
        """Determine if a file is binary.

        Args:
            path (str): Full path to the file to be tested.
            size (int, optional): Number of bytes read at a time to
                perform the test. As with :func:`io.RawIOBase.read`, if
                size is unspecified or -1, all bytes until EOF are
                returned. Defaults to 1024.

        :Design:
            For each chunk of the file, if any characters are left over
            after removing all text characters, the file is classified
            as 'binary', and ``True`` is returned immediately. For
            efficiency, only (N) bytes of the files are read at a time,
            as controlled by the ``size`` argument. Once a file is found
            to be binary, the function returns immediately as there is
            no need to continue reading.

        :References:

            - `How to detect if a file is binary <so_ref1_>`_
            - `ASCII printable character reference <so_ref2_>`_

            .. _so_ref1: https://stackoverflow.com/a/7392391/6340496
            .. _so_ref2: https://stackoverflow.com/a/32184831/6340496

        Returns:
            bool: True if a file is binary, otherwise False if the file
            is plain-text.

        """
        if not os.path.isfile(path):
            return True  # Non-files are considered binary.
        with open(os.path.realpath(path), 'rb') as f:
            while chunk := f.read(size):
                if bool(set(chunk) - cls._TEXTCHARS):
                    return True
        return False

    @classmethod
    def istext(cls, path: str, size: int=1024) -> bool:
        """Determine if a file is plain-text.

        Args:
            path (str): Full path to the file to be tested.
            size (int, optional): Number of bytes read to perform
                the test. As with :func:`io.RawIOBase.read`, if size is
                unspecified or -1, all bytes until EOF are returned.
                Defaults to 1024.

        :Design:
            This function simply calls the :meth:`isbinary` method and
            inverts the return value.

        Returns:
            bool: True if a file is plain-text, otherwise false if the
            file is binary.

        """
        return not cls.isbinary(path=path, size=size)

    @classmethod
    def iszip(cls, path: str) -> bool:
        r"""Determine if a file is a ``ZIP`` archive.

        Args:
            path (str): Full path to the file to be tested.

        Note:
            A file is tested to be a ``ZIP`` archive by checking the
            `first four bytes <zip-format_>`_ of the file itself, *not*
            using the file extension.

            It is up to the caller to handle empty or spanned ZIP
            archives appropriately.

        Returns:
            bool: True if the first four bytes of the file match any of
            the below. Otherwise, False.

            - ``\x50\x4b\x03\x04``: 'Standard' archive
            - ``\x50\x4b\x05\x06``: Empty archive
            - ``\x50\x4b\x07\x08``: Spanned archive

        .. _zip-format: https://en.wikipedia.org/wiki/ZIP_(file_format)#Local_file_header

        """
        with open(path, 'rb') as f:
            return f.read(4) in (cls._ZIPSIG, cls._ZIPSIG_EMPTY, cls._ZIPSIG_SPAN)


utilities = Utilities
