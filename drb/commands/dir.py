from __future__ import unicode_literals

import click
import os
import codecs
import glob
from drb.spectemplate import DoubleDelimiterTemplate
import logging
from drb.which import which
from drb.spawn import sp
from drb.path import getpath

@click.command()
@click.argument("imagetag", type=click.STRING)
@click.argument("source_directory", type=click.Path(exists=True, file_okay=False, resolve_path=True))
def dir(imagetag, source_directory):
    # TODO: let spectemplate and/or spec be optional parameters
    # TODO: let the user choose $-delimited templates
    deletespec = False
    spectemplates = glob.glob1(source_directory, "*.spectemplate")
    specfiles = glob.glob1(source_directory, "*.spec")
    if len(spectemplates) > 1:
        raise ValueError("More than one spectemplate found in source directory")

    if spectemplates:
        if specfiles:
            raise ValueError("Found both .spec and .spectemplate in source directory.")
        spectemplate = spectemplates[0]
        template = DoubleDelimiterTemplate(codecs.open(spectemplate, "rb", "utf-8").read())
        with_substitutions = template.substitute(os.environ)
        finalspec = os.path.splitext(spectemplate)[0] + ".spec"
        with codecs.open(finalspec, "wb", "utf-8") as f:
            f.write(with_substitutions)
        specfiles.append(finalspec)
        deletespec = True

    if not specfiles or len(specfiles) > 1:
        raise ValueError("No specfiles or more than one specfile in source directory")

    specfile = specfiles[0]

    # FIXME: delete written specfile if using a spectemplate
    logging.info("Now building project from %s on image %s", source_directory, imagetag)
    # TODO: let this be something more configurable and/or injected
    dockerexec = which("docker")
    try:
    # docker run $* -v ${CURRENTDIR}/dockerscripts:/dockerscripts -v ${SRCDIR}:/src -w /dockerscripts ${IMAGETAG} ./rpmbuild-in-docker.sh $(id -u):$(id -g)
        sp("{0} run -v {1}:/dockerscripts -v {2}:/src -w /dockerscripts {3} ./rpmbuild-in-docker.sh {4}:{5}",
        dockerexec, getpath("drb/dockerscripts"), source_directory, imagetag, os.getuid(), os.getgid())
    finally:
        if deletespec:
            os.unlink(specfile)





