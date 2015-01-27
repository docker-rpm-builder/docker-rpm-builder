# -*- coding: utf-8 -*-
import base64
def provide_encoded_signature(sign_with):
    sign_with_encoded = ""
    if sign_with:
        sign_with_encoded = base64.encodestring(open(sign_with, "r").read()).replace("\n", "")
    return sign_with_encoded
