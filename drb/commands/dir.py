from __future__ import unicode_literals

import os
import codecs
import glob
import logging

import click

from drb.spectemplate import DoubleDelimiterTemplate
from drb.which import which
from drb.spawn import sp
from drb.path import getpath


@click.command()
@click.argument("imagetag", type=click.STRING)
@click.argument("source_directory", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.argument("target_directory", type=click.Path(file_okay=False, resolve_path=True))
@click.argument("additional_docker_options", type=click.STRING, nargs=-1)
def dir(imagetag, source_directory, target_directory, additional_docker_options):
    """Builds a binary RPM from a directory.

    IMAGETAG should be a docker image id or a repository:tag,
    e.g something like a682b68bbaba or alanfranz/drb-epel-6-x86-64:latest

    SOURCE_DIRECTORY should be a directory containing the .spec or the
    .spectemplate file and all the source files and patches referenced
    in such spec.

    TARGET_DIRECTORY is where the RPMS will be written. Anything inside
    may be overwritten during the build phase.

    ADDITIONAL_DOCKER_OPTIONS whatever is passed will be forwarded
    straight to docker. PLEASE REMEMBER to insert a double dash (--)
    before the first additional options, otherwise it will be mistaken
    for a docker-rpm-builder option.

    example:

    docker-rpm-builder dir a682b68bbaba . -- --dns=10.2.0.1

    """

    # TODO: let spectemplate and/or spec be optional parameters
    # TODO: let the user choose $-delimited templates
    deletespec = False
    spectemplates = glob.glob1(source_directory, "*.spectemplate")
    specfiles = glob.glob1(source_directory, "*.spec")
    if len(spectemplates) > 1:
        raise ValueError("More than one spectemplate found in source directory")

    if not os.path.exists(target_directory):
        os.mkdir(target_directory)

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

    # downloading additional deps
    sp("build-deps/spectool -g {0}".format(finalspec))
    logging.info("Now building project from %s on image %s", source_directory, imagetag)
    # TODO: let this be something more configurable and/or injected
    dockerexec = which("docker")
    try:
        sp("{0} run -v {1}:/dockerscripts -v {2}:/src -w /dockerscripts {3} ./rpmbuild-in-docker.sh {4}:{5} {6}",
           dockerexec, getpath("drb/dockerscripts"), source_directory, imagetag, os.getuid(), os.getgid(), " ".join(additional_docker_options))
    finally:
        if deletespec:
            os.unlink(specfile)





