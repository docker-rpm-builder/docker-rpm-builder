from __future__ import unicode_literals

import os
from filecmp import cmp
import glob
import shutil
import logging
import click


from drb.configure_logging import configure_root_logger
from drb.docker import Docker
from drb.spectemplate import SpecTemplate
from drb.path import getpath
from drb.downloadsources import downloadsources
from drb.parse_ownership import parse_ownership
from drb.mkdir_p import mkdir_p
from drb.functional import one
from drb.exception_transformer import UserExceptionTransformer

_HELP = """Generates a spec file from a spectemplate. If the target specfile
    already exists and is identical, the target is untouched.

    docker-rpm-builder genspec SPECTEMPLATE TARGETSPEC
    
    SPECTEMPLATE should be a readable spectemplate path 

    TARGETSPEC should be a non-existing or writeable path
   
      Examples:

    docker-rpm-builder genspec tmux.spectemplate build-image/tmux.spec
    """

_logger = logging.getLogger("drb.commands.genspec")

@click.command(help=_HELP)
@click.argument("spectemplate", nargs=1, type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument("targetspec", nargs=1, type=click.Path(dir_okay=False, resolve_path=True))
@click.option('--verbose', is_flag=True, default=False)
def genspec(spectemplate, targetspec, verbose):
    configure_root_logger(verbose)

    rendered_filename = SpecTemplate.from_path(spectemplate).render(os.environ)
    mkdir_p(os.path.dirname(targetspec))
    if not os.path.exists(targetspec) or not cmp(rendered_filename, targetspec):
        shutil.copy(rendered_filename, targetspec)
    _logger.info("Spectemplate was rendered successfully. Your compiled spec is in %s", targetspec)










