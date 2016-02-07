# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from click import ClickException

import logging

class UserExceptionTransformer(object):
    """catches exceptions and presents an user-understandable error message"""

    def __init__(self, exc_class, message, append_original_message=False, final_message=""):
        self._exc_class = exc_class
        self._message = message
        self._append = append_original_message
        self._final_message = final_message
        self._logger = logging.getLogger(self.__class__.__name__)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return
        if exc_type == self._exc_class or issubclass(exc_type, self._exc_class):
            self._logger.exception("Full catched exception:")
            raise ClickException(self._message + ("\n" + exc_val.message if self._append else "") + self._final_message)
