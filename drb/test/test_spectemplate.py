from unittest import TestCase
from drb.spectemplate import DoubleDelimiterTemplate

class TestTemplateTransformation(TestCase):
    def test_templatetransformation(self):
        ddt = DoubleDelimiterTemplate("asd@{pippo}@xyz@pluto@what")
        result = ddt.safe_substitute({"pippo": "v1", "pluto": "v2"})
        self.assertEquals("asdv1xyzv2what", result)


