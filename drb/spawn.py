from __future__ import unicode_literals

from subprocess import Popen, PIPE
import warnings

class SpawnedProcessError(Exception):

    def __init__(self, returncode, cmd, output="", error=""):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
        self.error = error

    def __str__(self):
        return "Command '%s' returned non-zero exit status %d" % (self.cmd, self.returncode)

def sp(cmdformatstring, params=""):
    fullcmd = cmdformatstring.format(params)
    process = Popen(stdout=PIPE, stderr=PIPE, fullcmd)
    output, error = process.communicate()
    retcode = process.poll()
    if retcode:
        raise SpawnedProcessError(retcode, fullcmd, output=output, error=error)
    if error.strip():
        warnings.warn("Stderr data: {0}".format(error))
    return output
