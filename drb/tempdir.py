# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from tempfile import mkdtemp, gettempdir
from shutil import rmtree
import logging
import sys
import os

class TempDir(object):
    """A self-destroying temporary directory.

    Use the context manager

    Absolutely not threadsafe. Don't even think about it.
    """
    def __init__(self, prefix="/tmp/drb-temp."):
        self._tempdir = mkdtemp(prefix=prefix)
        self._was_deleted = False
        self._log = logging.getLogger("TempDir")

    @classmethod
    def platformwise(cls):
        """Returns a suitable temporary directory depending on the current platform.
        This usually means something in /tmp for linux and something in $HOME for OSX -
        since it's the home directory which gets mounted when using Kitematic/boot2docker
        /Docker Machine"""
        base_dir = os.path.expanduser("~") if sys.platform == "darwin" else gettempdir()
        return cls(prefix=os.path.join(base_dir, "drb-temp."))


    @property
    def path(self):
        return self._tempdir

    def delete(self):
        if not self._was_deleted:
            rmtree(self._tempdir, ignore_errors=True)
            if os.path.exists(self._tempdir):
                self.log.critical("Could not completely remove temporary dir %s", self._tempdir)    
            self._was_deleted = True


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.delete()


