import os
from drb.docker import Docker
from drb.path import getpath
from unittest import TestCase


REFERENCE_IMAGE = os.environ.get("REFERENCE_IMAGE") or "alanfranz/drb-epel-7-x86-64:latest"

class TestBasicIntegration(TestCase):

    def test_basic_docker_integration(self):
        image = REFERENCE_IMAGE
        testpath = getpath("drb/test")

        result = Docker().rm().bindmount_dir(testpath, "/testpath").image(image) \
                .cmd_and_args("/bin/bash", "-c", "cat /testpath/everythinglooksgood.txt").do_run()
        self.assertEquals("everything looks good", result.strip())
