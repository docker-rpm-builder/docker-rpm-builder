# -*- coding: utf-8 -*-
import logging
from drb.spawn import SpawnedProcessError

_logger = logging.getLogger("drb.pull")

def pull(dockerexec, image):
    try:
        sp("{dockerexec} pull {image}", **locals())
    except SpawnedProcessError, e:
        _logger.exception("Error while pulling docker image:")