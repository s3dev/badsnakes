#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides file collection functionality to the
            project.

            Specifically, this module is called by
            :class:`badsnakes.badsnakes.BadSnakes.main` to populate the
            'files list' which holds all files to be analysed.

            The CLI argument ``PATH`` is passed into this module, which
            then traverses either the list of files, the directory or
            extracts the wheel, in efforts to determine the files which
            should be analysed. These files are passed back to the caller
            via the :attr:`files` property.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

:Examples:

    Collect plain-text files from a given *directory*::

        >>> from badsnakes.libs.collector import Collector

        >>> c = Collector(paths=['/path/to/files'])
        >>> c.collect()
        >>> c.files

        [['/path/to/files/project.py',
          '/path/to/files/script.sh']]


    Collect plain-text files from a Python *wheel*::

        >>> from badsnakes.libs.collector import Collector

        >>> c = Collector(paths=['/path/to/project-0.7.3-py3-none-any.whl'])
        >>> c.collect()
        >>> c.files

        [['/tmp/tmpqnm6yka2/project/module00.py',
          '/tmp/tmpqnm6yka2/project/module01.py',
          '/tmp/tmpqnm6yka2/project/module02.py',
          ...,
          '/tmp/tmpqnm6yka2/project/script.sh',
          '/tmp/tmpqnm6yka2/project/file.txt',
          ...,
          '/tmp/tmpqnm6yka2/project/module08.py',
          '/tmp/tmpqnm6yka2/project/module09.py',
          '/tmp/tmpqnm6yka2/project/module10.py']]

"""
# pylint: disable=import-error

import logging
import os
import re
import tempfile
import zipfile
from glob import glob
# locals
from badsnakes.libs.config import systemcfg
from badsnakes.libs.utilities import utilities


class MixedTypesError(Exception):
    """Custom error class raised for mixed ``PATH`` type errors."""


class _CollectorBase:
    """Private base class providing file collection functionality.

    Args:
        path (str): Full path to the module, directory or wheel for
            collection.

    """

    def __init__(self, path: str):
        """Collector base class initialiser."""
        self._path = path
        self._files = []

    @property
    def files(self) -> list:
        """Accessor to the list of collected files."""
        return self._files

    def collect(self):
        """Collect all files for this class-type."""
        # Dummy method to be overridden by the specialising class.


class _CollectorDirectory(_CollectorBase):
    """Collect all files for analysis from the given directory.

    This *private* class is not part of the public interface. Please call the
    :class:`Collector` class instead.

    """

    def collect(self, path: str=None):
        """Collect all files for this class-type.

        Args:
            path (str, optional): Directory path. This argument was
                originally implemented for use by :class:`_CollectorWheel`
                to enable directory traversal using existing logic.
                Defaults to None.

        :Logic:

            1) Using ``glob.glob`` recursively, all files (including
               hidden files) are collected.

            2) Next, using ``filter`` remove any files which match the
               exclusion pattern and are not plain-text. See *Tip* below.

            3) Map ``os.path.realpath`` to all files to expand the
               filepaths.

        .. tip::

            The excluded directories are maintained by the list in
            ``config.toml`` under the ``system.exclude_dirs`` key.

        """
        path = path if path else self._path
        exclude = systemcfg['exclude_dirs']
        rexp = re.compile(f"({'|'.join(exclude)})")
        files = glob(os.path.join(path, '**'), include_hidden=True, recursive=True)
        files_ = filter(lambda x: (not rexp.search(x)) and utilities.istext(x), files)
        self._files = list(map(os.path.realpath, files_))


class _CollectorWheel(_CollectorBase):
    """Collect all files for analysis from a Python wheel.

    This *private* class is not part of the public interface. Please call the
    :class:`Collector` class instead.

    Args:
        path (str): Full path to the wheel file.

    """

    def __init__(self, path: str):
        """Wheel collector class initialiser."""
        super().__init__(path=path)
        self._tmpdir = None   # Used to keep the tmpdir object alive.

    @property
    def tmpdir(self) -> tempfile.TemporaryDirectory:
        """Accessor to the temporary directory object."""
        return self._tmpdir

    def collect(self):
        """Unzip a wheel file and collect files.

        :Logic:

            1) Create a temporary directory object (using ``tempfile``).

            2) Using ``zipfile``, unzip the wheel into the temporary
               directory.

            3) Create an instance of the :class:`_CollectorDirectory`
               class and pass the path to the temp directory into the
               class for file collection.

            4) Store the list of collected files into the :attr:`_files`
               attribute.

        :Temp Directory:
            The :class:`tempfile.TemporaryDirectory` object created by
            this method is *not* explicitly closed, as the directory must
            exist for analysing the files. Therefore, the temp directory
            is removed when the ``tmpdir`` object has been destroyed,
            generally on program completion.

            For this reason, the object must be kept 'alive' in the class
            instance, and therefore *cannot* be a local variable. To keep
            the object alive, the class' instance of the temp directory
            object is appended to a list in the parent class.

        """
        # pylint: disable=consider-using-f-string
        # pylint: disable=consider-using-with
        self._tmpdir = tempfile.TemporaryDirectory()  # No with to keep the object alive.
        with zipfile.ZipFile(file=self._path, mode='r') as zf:
            for f in zf.filelist:
                zf.extract(member=f, path=self._tmpdir.name)
        logging.debug('Unpacked wheel files (from %s):', self._tmpdir.name)
        logging.debug('%s', '\n\t '.join(map('- {}'.format,
                                             glob(os.path.join(self._tmpdir.name, '**'),
                                                  recursive=True,
                                                  include_hidden=True))))
        _c = _CollectorDirectory(path=None)
        _c.collect(path=self._tmpdir.name)
        self._files = _c.files


class Collector:
    """Primary file collection interface class.

    Args:
        paths (list): A list of file paths or directories from the
            argument parser.

    Note:
        On instantiation, all elements in the ``paths`` list argument are
        expanded to their realpath and tested to ensure they exist.

    """

    def __init__(self, paths: list):
        """File collector class initialiser."""
        self._paths = paths if isinstance(paths, (list, tuple)) else [paths]
        self._paths = list(map(os.path.realpath, self._paths))
        self._files = []    # Files to be processed.
        self._tmpdirs = []  # Used to keep the wheel's temp dir object alive.
        self._checks()

    @property
    def files(self) -> list:
        """Accessor to the list of Python files to be analysed.

        Note:
            This property is a *list of lists*.

            Each outer list represents a wheel or a directory, with each
            inner list representing the files contained therein.

        """
        return self._files

    def collect(self):
        """Collect files for analysis from the provided paths.

        :Criteria:
            Using the private :meth:`_identify` method, the file
            collection is routed to the appropriate file collector based
            on the type of path provided to the ``paths`` argument on
            instantiation.

            - **Directory**: All paths in the :attr:`_paths` attribute
              must be directories.

            - **Module**: All paths in the :attr:`_paths` attribute must
              be plain-text files.

            - **Wheel**: All paths in the :attr:`_paths` attributes must
              be Python wheels, or zip files.

            Only files of the same type (directory, module or wheel) can
            be collected at the same time, otherwise a ``ValueError`` is
            raised.

        Raises:
            MixedTypesError: Raised if the :attr:`_paths` attribute contains
                a mix of the types listed above.

        """
        match self._identify():
            case 'dir':
                self._collect_from_directory()
            case 'modules':
                self._collect_from_files()
            case 'wheel':
                self._collect_from_wheel()
            case _:
                msg = ('Invalid file types (or mix of file types) provided. '
                       'All files provided must be of the same type (module, wheel or directory).')
                # raise ValueError(msg)
                raise MixedTypesError(msg)

    def _checks(self):
        """Perform pre-collection checks.

        :Checks:
            - All files exist.

        Raises:
            FileNotFoundError: Raised if any file in ``paths`` does not
                exist.

        """
        for p in self._paths:
            if not os.path.exists(p):
                raise FileNotFoundError(f'File not found: {p}')

    def _collect_from_directory(self):
        """Collect all plain-text files from a directory.

        Before this method is called, all paths are tested to ensure
        they are directories.

        """
        logging.debug('Collecting files from a directory ...')
        for dir_ in self._paths:
            c = _CollectorDirectory(path=dir_)
            c.collect()
            self._files.append(c.files)

    def _collect_from_files(self):
        """Collect all plain-text files.

        As the realpath conversion and file exists check have already
        been performed, this method can simply append the :attr:`_paths`
        argument to :attr:`_files`, for the caller's use.

        """
        logging.debug('Collecting files from modules ...')
        self._files.append(self._paths)

    def _collect_from_wheel(self):
        """Collect all plain-text files from wheels.

        Before this method is called, all paths are tested to ensure
        they are wheels (or .zip files).

        """
        logging.debug('Collecting files from wheels ...')
        for wheel in self._paths:
            c = _CollectorWheel(path=wheel)
            c.collect()
            self._files.append(c.files)
            self._tmpdirs.append(c.tmpdir)  # Keep the tmpdir object alive.

    def _identify(self) -> str:
        """Identify the type of collection to take place.

        Returns:
            str: One of the following strings are returned, based on the
            content of the ``paths`` argument:

                - Directory: 'dir'
                - Python modules: 'modules'
                - Wheel: 'wheel'
                - Anything else: 'invalid'

        """
        # These tests are ordered by fastest to slowest.
        if self._isdir():
            return 'dir'
        if self._iswheel():
            return 'wheel'
        if self._istext():
            return 'modules'
        return 'invalid'

    def _isdir(self) -> bool:
        """Test if *all* elements of ``paths`` are directories.

        Returns:
            bool: True if *all* paths are directories, otherwise False.

        """
        return all(map(os.path.isdir, self._paths))

    def _istext(self) -> bool:
        """Test if *all* elements of ``paths`` are plain-text files.

       Returns:
            bool: True if *all* elements of ``paths`` are plain-text
            files, otherwise False.

        """
        # return not any(map(utilities.isbinary, self._paths))
        return all(map(utilities.istext, self._paths))

    def _iswheel(self) -> bool:
        """Test if *all* elements of ``paths`` are Python wheels.

        Note:
            A file is tested as a wheel by checking the first four bytes
            of the file itself, *not* using the file extension. As such
            a ``.zip`` file will pass this test as well.

        Returns:
            bool: True if *all* elements of ``paths`` are Python wheels
            (or ZIP archives), otherwise False.

        """
        if all(map(os.path.isfile, self._paths)):  # Required to raise mixed-types error.
            return all(map(utilities.iszip, self._paths))
        return False
