# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import base64

def serialize(d):
    joined = ";".join("export {0}='{1}'".format(k, "{0}".format(v).replace("'", "'\\''")) for k,v in d.iteritems())
    # arbitrary encoding, but I'll use ASCII -which is safe- until we need something better.
    return base64.encodestring(joined.encode("ascii")).replace(b"\n", b"")



