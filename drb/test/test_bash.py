# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from unittest import TestCase
from drb.bash import serialize
from collections import OrderedDict
import base64

class TestSerialization(TestCase):
    def test_serialized_is_bytestring(self):
        d = OrderedDict()
        d["ASD"] = "pippo"
        serialized = serialize(d)
        self.assertTrue(isinstance(serialized, bytes))

    def test_serialization(self):
        d = OrderedDict()
        d["ASD"] = "pippo"
        d["WHAT"] = "pippo\n"
        d["ESCAPE"] = "pippo'"
        serialized = serialize(d)
        v = base64.decodestring(serialized)
        self.assertEquals(b"export ASD='pippo';export WHAT='pippo\n';export ESCAPE='pippo'\\'''", v)


