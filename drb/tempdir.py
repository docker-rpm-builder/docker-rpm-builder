# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from tempfile import mkdtemp
from shutil import rmtree
import logging
from weakref import ref

class TempDir(object):
    """A self-destroying temporary directory.

    Use the context manager

    Absolutely not threadsafe. Don't even think about it.
    """
    def __init__(self, prefix="/tmp/drbtemp.XXXXX"):
        self._tempdir = mkdtemp(prefix=prefix)
        self._was_deleted = False
        self._log = logging.getLogger("TempDir")

    @property
    def path(self):
        return self._tempdir

    def _delete(self):
        if not self._was_deleted:
            rmtree(self._tempdir, onerror=lambda *args, **kwargs: self._log.critical("Could not completely remove temporary directory %s", self._tempdir))
            self._was_deleted = True


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._delete()


