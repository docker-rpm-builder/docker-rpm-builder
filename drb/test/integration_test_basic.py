import os
from drb.path import getpath
from drb.spawn import sp
from drb.which import which
from unittest2 import TestCase


REFERENCE_IMAGE = "alanfranz/drb-epel-7-x86-64:latest"

class TestBasicIntegration(TestCase):

    def test_basic_docker_integration(self):
        image = REFERENCE_IMAGE
        dockerexec = which("docker")
        testpath = getpath("drb/test")
        result = sp("{dockerexec} run --rm -v {testpath}:/testpath {image} /bin/bash -c 'cat /testpath/everythinglooksgood.txt'", **locals())
        self.assertEquals("everything looks good", result.strip())

    def test_docker_scripts_permissions(self):
        for fn in os.listdir(getpath("drb/dockerscripts")):
            self.assertTrue(os.access(os.path.join(getpath("drb/dockerscripts"), fn), os.X_OK), "File {0} is not executable, probably an install error has happened. Make sure you're using a recent python+virtualenv".format(fn))



