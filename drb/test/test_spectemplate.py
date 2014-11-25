# -*- coding: utf-8 -*-

from unittest import TestCase
from drb.spectemplate import DoubleDelimiterTemplate

class TestTemplateTransformation(TestCase):
    def test_templatetransformation_from_string(self):
        ddt = DoubleDelimiterTemplate("asd@{pippo}@xyz@pluto@what")
        result = ddt.safe_substitute({"pippo": "v1", "pluto": "v2"})
        self.assertEquals("asdv1xyzv2what", result)

    def test_templatetransformation_from_unicode(self):
        ddt = DoubleDelimiterTemplate(u"ààasd@{pippo}@xyz@pluto@what")
        result = ddt.safe_substitute({u"pippo": u"v1", u"pluto": u"v2ù"})
        self.assertEquals(u"ààasdv1xyzv2ùwhat", result)


