# -*- coding: utf-8 -*-
from __future__ import unicode_literals

def provide_encoded_signature(signature_file):
    sign_with_encoded = ""
    if signature_file:
        sign_with_encoded = open(signature_file, "r").read().replace("\n", "\\n") #use a literal \n to be interpreted by echo later on.
    return sign_with_encoded

