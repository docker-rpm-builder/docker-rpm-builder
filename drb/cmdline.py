import os
from pkgutil import iter_modules
from importlib import import_module

import click
click.disable_unicode_literals_warning = True

from . import commands

@click.group()
def cmdline():
    pass

def autoload_commands(group, source_package):
    """
    autoloads to group from source package. the click.command() wrapped function
    MUST be called just like the module.

    :param group: click.group where to add autoloaded scripts
    :param source_package: the package from where to autoload things
    """
    for loader, name, ispackage in iter_modules([os.path.dirname(source_package.__file__)]):
        module = import_module("{0}.{1}".format(source_package.__name__, name))
        group.add_command(getattr(module, name))


autoload_commands(cmdline, commands)






