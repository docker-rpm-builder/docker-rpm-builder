from string import Template

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

__all__ = ("DoubleDelimiterTemplate", )
