from __future__ import unicode_literals

from subprocess import Popen, PIPE, STDOUT, call
import logging

class SpawnedProcessError(Exception):

    def __init__(self, returncode, cmd, output="", error=""):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
        self.error = error

    def __str__(self):
        return "Command '%s' returned non-zero exit status %d:\n%s\n%s\n" % (self.cmd, self.returncode, self.output, self.error)

def sp(cmdformatstring, *params, **kwargs):
    fullcmd = cmdformatstring.format(*params, **kwargs)
    logging.debug("Now executing:\n%s\n", fullcmd)
    process = Popen(fullcmd, stdout=PIPE, stderr=PIPE, shell=True)
    output, error = process.communicate()
    retcode = process.poll()
    if retcode:
        raise SpawnedProcessError(retcode, fullcmd, output=output, error=error)
    return output
