# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import logging
from datetime import datetime
import tzlocal

def posix2local(timestamp, tz=tzlocal.get_localzone()):
    """Seconds since the epoch -> local time as an aware datetime object."""
    return datetime.fromtimestamp(timestamp, tz)

# idea is courtesy of J.F. Sebastian; prevents a nasty Python2 timezone-naivety issue.
class Formatter(logging.Formatter):
    def converter(self, timestamp):
        return posix2local(timestamp)

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            t = dt.strftime(self.default_time_format)
            s = self.default_msec_format % (t, record.msecs)
        return s

def configure_root_logger(debug=False):
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s", "%Y-%m-%dT%H:%M:%S%z"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

