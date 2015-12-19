# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from click import ClickException

class UserExceptionTransformer(object):
    """catches exceptions and presents an user-understandable error message"""
    def __init__(self, exc_class, message, append_original_message=False):
        self._exc_class = exc_class
        self._message = message
        self._append = append_original_message

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return
        if exc_type == self._exc_class or issubclass(exc_type, self._exc_class):
            raise ClickException(self._message + ("\n" + exc_val.message if self._append else ""))
