# -*- coding: utf-8 -*-

import sys

import click
from drb.path import getpath
from unittest2 import TestLoader, TextTestRunner, TestSuite

_HELP = """
Perform a selftest.

--full can be passed to run the full test suite - may take a very long time,
especially at the first run when it's required to download all the images that
get tested along this tool.

"""

@click.command(help=_HELP)
@click.option("--full", is_flag=True)
def selftest(full=False):
    # TODO: run unitests as well here
    click.echo("Starting self test. May take a lot of time, especially the first time it is launched. Requires networking.")

    loader = TestLoader()
    all_suites = [loader.discover(getpath("."))]

    integration_test_pattern = "integration_test_*" if full else "integration_test_basic.py"
    all_suites.append(loader.discover(getpath("."), pattern=integration_test_pattern))

    runner = TextTestRunner(verbosity=2)
    result = runner.run(TestSuite(all_suites))

    if not result.wasSuccessful():
        click.echo("Self test failed. Checklist:\n\nVerify the docker service is running\n"
                   "Verify the 'docker' group exists and your user belongs to it\n"
                   "If you had to add the group, verify you've restarted the 'docker' service after such addition\n"
                   "Verify you've logged out+in after adding your user to the group\n"
                   "Verify selinux is disabled\n"
                   "Verify your disk has enough free space\n")
        sys.exit(1)

    click.echo("Self test succeeded.")
