# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
from drb.spawn import sp
from drb.which import which
from drb.path import getpath

_logger = logging.getLogger("drb.downloadsources")

def downloadsources(source_directory, specfile):
    _logger.info("Downloading additional sources")
    spectool = which("spectool")
    if spectool is None:
        _logger.warning("spectool not found in path, will use bundled version; it might not work")
        spectool = getpath("drb/builddeps/spectool")
    sp("{0} --get-files --directory {1} {2}".format(spectool, source_directory, specfile))
