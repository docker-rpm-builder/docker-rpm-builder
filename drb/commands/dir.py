from __future__ import unicode_literals

import os
import codecs
import glob
import logging
import base64

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
@click.option("--download-sources", is_flag=True)
@click.option("--bash-on-failure", is_flag=True)
@click.option("--sign-with", nargs=1, type=click.Path(exists=True, dir_okay=False, resolve_path=True))
def dir(imagetag, source_directory, target_directory, additional_docker_options, download_sources=False,
        bash_on_failure=False, sign_with=None):
    """Builds a binary RPM from a directory.

    IMAGETAG should be a docker image id or a repository:tag,
    e.g something like a682b68bbaba or alanfranz/drb-epel-6-x86-64:latest

    SOURCE_DIRECTORY should be a directory containing the .spec or the
    .spectemplate file and all the source files and patches referenced
    in such spec. If using a .spectemplate the directory should be writeable,
    as a .spec file will be written there (and then removed).

    TARGET_DIRECTORY is where the RPMS will be written. Anything inside
    may be overwritten during the build phase.

    ADDITIONAL_DOCKER_OPTIONS whatever is passed will be forwarded
    straight to docker. PLEASE REMEMBER to insert a double dash (--)
    before the first additional options, otherwise it will be mistaken
    for a docker-rpm-builder option.

    if --download-sources is enabled, SourceX and PatchX from the spec
    that contain an URL will be downloaded from the internet. Such
    files will be placed in SOURCE_DIRECTORY, that should be writeable,
    hence. They won't be deleted afterwards. WARNING: if an item is already
    there and it's different/older, it will be overwritten without asking;
    wget's timestamping options is used for such purpose.

    if --bash-on-failure is enabled, the tool will drop in an interactive
    shell if the build fails.

    if --sign-with is passed, the chosen GPG key is used to sign the package.


    example:

    docker-rpm-builder dir a682b68bbaba . /tmp/rpms -- --dns=10.2.0.1

    """

    # TODO: let spectemplate and/or spec be optional parameters
    # TODO: let the user choose $-delimited templates
    deletespec = False
    spectemplates = [os.path.join(source_directory, fn) for fn in glob.glob1(source_directory, "*.spectemplate")]
    specfiles = [os.path.join(source_directory, fn) for fn in glob.glob1(source_directory, "*.spec")]
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

    # downloading additional deps; those get into the source_directory. should we add
    # an option for that?
    if download_sources:
        logging.info("Downloading additional sources")
        sp("{0} --get-files --directory {1} {2}".format(getpath("drb/builddeps/spectool"), source_directory, specfile))

    logging.info("Now building project from %s on image %s", source_directory, imagetag)
    dockerexec = which("docker")

    bashonfail = "dontspawn"
    bashonfail_options = ""
    if bash_on_failure:
        bashonfail = "bashonfail"
        bashonfail_options = "-i -t"

    sign_with_encoded = ""
    if sign_with:
        sign_with_encoded = base64.encodestring(open(sign_with, "r").read()).replace("\n", "")

    try:
        sp("{0} run -v {1}:/dockerscripts -v {2}:/docker-rpm-build-root/SOURCES -v {7}:/docker-rpm-build-root/RPMS {9} -w /dockerscripts {3} ./rpmbuild-dir-in-docker.sh {4} {5} {8} {10} {6}",
           dockerexec, getpath("drb/dockerscripts"), source_directory, imagetag, os.getuid(), os.getgid(), " ".join(additional_docker_options),
           target_directory, bashonfail, bashonfail_options, sign_with_encoded)
    finally:
        if deletespec:
            os.unlink(specfile)





