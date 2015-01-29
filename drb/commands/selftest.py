# -*- coding: utf-8 -*-

import click
import sys
import os
from subprocess import Popen
from drb.spawn import sp
from drb.which import which
from drb.path import getpath


_HELP = """
Perform a selftest.

ADDITIONAL_TEST_OPTIONS will be passed straight to the integration_test script
for the full test

--full can be passed to run the full test suite - may take a very long time,
especially at the first run when it's required to download all the images that
get tested along this tool.

"""

@click.command(help=_HELP)
@click.option("--full", is_flag=True)
@click.argument("additional_test_options", type=click.STRING, nargs=-1)
def selftest(additional_test_options, full=False):
    short_test()
    if full:
        long_test(additional_test_options)



def short_test():
    # TODO: run unitests as well here
    click.echo("Starting short self test")

    dockerexec = which("docker")
    result = sp("{dockerexec} run phusion/baseimage /bin/bash -c 'echo everything looks good'", **locals())
    if result.strip() != "everything looks good":
        click.echo("Basic self test failed: docker run failed:\n'%s'" % result)
        sys.exit(1)

    spectoolout = sp("{0} -h 2>&1".format(getpath("drb/builddeps/spectool")))
    if not "Usage: spectool [<options>] <specfile>" in spectoolout:
        click.echo("Basic self test failed, could not run spectool (missing perl?)\n%s" % spectoolout)
        sys.exit(1)

    click.echo("Short self test succeeded.")

def long_test(additional_test_options):
    click.echo("Starting full test suite. May take a long time, especially the first time, since docker will be downloading lot of data.")
    test_script = getpath("drb/integration_tests/test.sh")
    additional_test_options = " ".join(additional_test_options)
    os.chdir(getpath("drb/integration_tests"))
    p = Popen("{test_script} {additional_test_options}".format(**locals()), shell=True)
    exitcode = p.wait()
    if exitcode == 0:
        click.echo("Full test completed successfully.")
    else:
        click.echo("Full test failed.")
        sys.exit(1)
