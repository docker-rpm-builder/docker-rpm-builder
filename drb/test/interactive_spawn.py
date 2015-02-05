# -*- coding: utf-8 -*-

from unittest2 import TestCase
from drb.bash import spawn_interactive

out = spawn_interactive("/bin/bash")

print "output was:", out