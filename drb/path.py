# -*- coding: utf-8 -*-

from . import uriresolver

def getpath(path):
    return uriresolver.resource_filename_resolver("req://drb/{0}".format(path))

