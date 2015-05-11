# -*- coding: utf-8 -*-

import click
import sys
import os
import shutil
from subprocess import Popen
from tempfile import mkdtemp
from drb.spawn import sp
from drb.which import which
from drb.path import getpath
from drb.downloadsources import downloadsources


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
    click.echo("Starting short self test. Requires networking and may take a bit of time especially at the first run, because data will be downloaded")

    dockerexec = which("docker")
    testpath = getpath("drb/test")
    result = sp("{dockerexec} run --rm -v {testpath}:/testpath phusion/baseimage /bin/bash -c 'cat /testpath/everythinglooksgood.txt'", **locals())
    if result.strip() != "everything looks good":
        click.echo("Basic self test failed: docker run failed. Checklist:\n\nVerify the docker service is running\n"
                   "Verify the 'docker' group exists and your user belongs to it\n"
                   "If you had to add the group, verify you've restarted the 'docker' service after such addition\n"
                   "Verify you've logged out+in after adding your user to the group\n"
                   "Verify selinux is disabled\n"
                   "Verify your disk has enough free space\n"
                   "Error:\n%s\n" % result)
        sys.exit(1)

    tmpdir = mkdtemp()
    try:
        downloadsources(tmpdir, getpath("drb/test/spectooltest.spec"), "alanfranz/drb-epel-6-x86-64:latest")
        if not os.path.exists(os.path.join(tmpdir, "README.md")):
            click.echo("Basic self test failed, could not download sources")
            sys.exit(1)
    finally:
        shutil.rmtree(tmpdir)

    for fn in os.listdir(getpath("drb/dockerscripts")):
        if not os.access(os.path.join(getpath("drb/dockerscripts"), fn), os.X_OK):
            click.echo("File {0} is not executable, probably an install error has happened. Make sure you're using a recent python+virtualenv".format(fn))
            sys.exit(1)

    click.echo("Short self test succeeded.")

def long_test(additional_test_options):
    click.echo("Starting full test suite. Requires networking and may take a long time, especially the first time, since docker will be downloading lot of data.")
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
