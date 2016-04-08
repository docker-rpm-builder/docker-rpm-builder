# -*- coding: utf-8 -*-

from unittest import TestCase

from drb.spectemplate import DoubleDelimiterTemplate, SpecTemplate
from tempfile import NamedTemporaryFile
from StringIO import StringIO

class TestTemplateTransformation(TestCase):
    def test_templatetransformation_from_string(self):
        ddt = DoubleDelimiterTemplate("asd@{pippo}@xyz@pluto@what")
        result = ddt.safe_substitute({"pippo": "v1", "pluto": "v2"})
        self.assertEquals("asdv1xyzv2what", result)

    def test_template_ignores_single_at(self):
        ddt = DoubleDelimiterTemplate("* Wed Sep 26 2012 Ryan O'Hara <rohara@redhat.com> - 1.2.7-3")
        result = ddt.substitute({})
        self.assertEquals("* Wed Sep 26 2012 Ryan O'Hara <rohara@redhat.com> - 1.2.7-3", result)

    def test_templatetransformation_from_unicode(self):
        ddt = DoubleDelimiterTemplate(u"ààasd@{pippo}@xyz@pluto@what")
        result = ddt.safe_substitute({u"pippo": u"v1", u"pluto": u"v2ù"})
        self.assertEquals(u"ààasdv1xyzv2ùwhat", result)

class TestSpecTemplate(TestCase):
    def test_spectemplate(self):
        tmp = NamedTemporaryFile()
        tmp.write("aaaa @VARIABLE@ cccc @SOMETHING@ eeee")
        tmp.flush()

        st = SpecTemplate.from_path(tmp.name)

        rendered = st.render({"VARIABLE": "bbbb", "SOMETHING": "dddd"})

        self.assertEquals("aaaa bbbb cccc dddd eeee", open(rendered).read())


