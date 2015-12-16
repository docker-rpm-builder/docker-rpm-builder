# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import base64


def serialize(d):
    joined = ";".join("export {0}='{1}'".format(k, "{0}".format(v).replace("'", "'\\''")) for k,v in d.iteritems())
    # arbitrary encoding, but I'll use ASCII -which is safe- until we need something better.
    return base64.encodestring(joined.encode("ascii")).replace(b"\n", b"")


def provide_encoded_signature(signature_file):
    sign_with_encoded = ""
    if signature_file:
        sign_with_encoded = open(signature_file, "r").read().replace("\n", "\\n") #use a literal \n to be interpreted by echo later on.
    return sign_with_encoded

