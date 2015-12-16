# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import base64
from subprocess import Popen
import logging
#from drb.spawn import SpawnedProcessError

def serialize(d):
    joined = ";".join("export {0}='{1}'".format(k, "{0}".format(v).replace("'", "'\\''")) for k,v in d.iteritems())
    # arbitrary encoding, but I'll use ASCII -which is safe- until we need something better.
    return base64.encodestring(joined.encode("ascii")).replace(b"\n", b"")


def provide_encoded_signature(signature_file):
    sign_with_encoded = ""
    if signature_file:
        sign_with_encoded = open(signature_file, "r").read().replace("\n", "\\n") #use a literal \n to be interpreted by echo later on.
    return sign_with_encoded

def spawn_interactive(cmdformatstring, *params, **kwargs):
    fullcmd = cmdformatstring.format(*params, **kwargs)
    logging.debug("Now interactively executing:\n%s\n", fullcmd)
    process = Popen(["/bin/bash", "-i", "-c" , fullcmd], stdin=0, stdout=1, stderr=2)
    output, error = process.communicate()
    retcode = process.poll()
    if retcode:
        raise SpawnedProcessError(retcode, fullcmd)
