# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# just a runtime assertion which is not deleted at runtime by optimized python parameters.
class PreconditionFailed(Exception):
    pass

def precondition(expr, message="", *parameters):
    if not expr:
        raise PreconditionFailed(message.format(parameters))
