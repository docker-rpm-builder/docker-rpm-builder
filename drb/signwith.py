# -*- coding: utf-8 -*-
import base64
def provide_encoded_signature(sign_with):
    sign_with_encoded = ""
    if sign_with:
        sign_with_encoded = open(sign_with, "r").read().replace("\n", "\\n") #use a literal \n to be interpreted by echo later on.
    return sign_with_encoded
