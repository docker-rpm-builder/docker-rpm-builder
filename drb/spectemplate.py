from collections import Mapping
from string import Template
from tempfile import NamedTemporaryFile, gettempprefix

import sys

from drb import dbc
import codecs
import os
from drb.tempdir import TempDir


class DoubleDelimiterTemplate(Template):
    """A string class for supporting @ID@ and @{ID}@-substitutions.
    """

    delimiter = '@'
    idpattern = r'[_a-z][_a-z0-9]*'

    pattern = r"""
    %(delim)s(?:
      (?P<escaped>%(delim)s) |   # Escape sequence of two delimiters
      (?P<named>%(id)s)%(delim)s      |   # delimiter and a Python identifier
      {(?P<braced>%(id)s)}%(delim)s   |   # delimiter and a braced identifier
      (?P<invalid>coiaud89usad90wq)              # Other ill-formed delimiter exprs
    )
    """ % {"delim":delimiter, "id":idpattern}

    def __init__(self, template):
        self.template = template


class SpecTemplate(object):
    def __init__(self, spectemplate_reader):
        self._ddtemplate = DoubleDelimiterTemplate(spectemplate_reader.read())

    @classmethod
    def from_path(cls, spectemplate_path):
        dbc.precondition(os.access(spectemplate_path, os.R_OK), "Spectemplate path must be readable, {0} isn't", spectemplate_path)
        with codecs.open(spectemplate_path, "rb", "utf-8") as f:
            s = SpecTemplate(f)
        return s

    def render(self, substitution_mapping):
        dbc.precondition(isinstance(substitution_mapping, Mapping), "Substitution mapping must be a Mapping instance")
        with_substitutions = self._ddtemplate.substitute(substitution_mapping)
        rendered = NamedTemporaryFile(suffix=".spec", prefix=os.path.expanduser("~") if sys.platform == "darwin" else gettempprefix())
        rendered.write(with_substitutions)
        rendered.flush()
        return rendered






__all__ = ("SpecTemplate", )
