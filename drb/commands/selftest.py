# -*- coding: utf-8 -*-

import click
import sys
import os
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
    if full:
        long_test(additional_test_options)
    else:
        short_test()


def short_test():
    dockerexec = which("docker")
    result = sp("{dockerexec} run phusion/baseimage /bin/bash -c 'echo everything looks good'", **locals())
    if result.strip() != "everything looks good":
        click.echo("Basic self test failed: got '%s'" % result)
        sys.exit(1)
    click.echo("Basic self test succeeded.")

def long_test(additional_test_options):
    test_script = getpath("drb/integration_tests/test.sh")
    click.echo("Now running full test suite. May take a long time.")
    additional_test_options = " ".join(additional_test_options)
    os.chdir(getpath("drb/integration_tests"))
    sp("{test_script} {additional_test_options}", **locals())
    click.echo("Full test completed successfully.")
