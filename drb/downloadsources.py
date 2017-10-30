# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import pipes

import codecs
from itertools import takewhile

from drb.docker import Docker
from drb.tempdir import TempDir
from drb.which import which
import os
import re

_logger = logging.getLogger("drb.downloadsources")

from subprocess import Popen, PIPE, STDOUT, call
import logging

_MY_EOF_MARKER = "DOCKER_RPM_BUILDER_PRIVATE_EOF"

class Box(object):
    value = None

class SpawnedProcessError(Exception):
    def __init__(self, returncode, cmd, output="", error=""):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
        self.error = error

    def __str__(self):
        return "Command '%s' returned non-zero exit status %d:\n%s\n%s\n" % (self.cmd, self.returncode, self.output, self.error)

def sp(cmdformatstring, *params, **kwargs):
    fullcmd = cmdformatstring.format(*params, **kwargs)
    logging.debug("Now executing:\n%s\n", fullcmd)
    process = Popen(fullcmd, stdout=PIPE, stderr=PIPE, shell=True)
    output, error = process.communicate()
    retcode = process.poll()
    if retcode:
        raise SpawnedProcessError(retcode, fullcmd, output=output, error=error)
    return output


def downloadsources(source_directory, specfilename, target_image):
    """Leverages rpmbuild to complete the macros in a spec file, then
    uses wget to fetch source and patch files."""
    _logger.info("Downloading additional sources")

    lines = get_spec_with_resolved_macros(specfilename, target_image)
    urls = get_source_and_patches_urls(lines)
    download_files(urls, source_directory)

def get_spec_with_resolved_macros(specfilename, target_image):
    lines_upto_prep = list(takewhile(lambda line: not line.startswith("%prep"),
                                    codecs.open(specfilename, encoding="utf-8")))

    for line in lines_upto_prep:
        if _MY_EOF_MARKER in line:
            raise ValueError("Private EOF marker mustn't exist already inside specfile.")

    with TempDir.platformwise() as tmpdir:
        tempspec_path = os.path.join(tmpdir.path, os.path.basename(specfilename))
        tempspec = codecs.getwriter("utf-8")(open(tempspec_path, "wb"))
        # it looks like there can be a lot of things until %prep that make little sense to us...
        # we just drop %package/%description XXXX parts right now, since they seem to interfere with our
        # macro resolution system...
        # RETHINK: maybe we want to write everything in the spec file (all macros, especially) BUT what is
        # in ANY section (the %prep was a kind of stop marker - although I suspect %global and %define could
        # just exist wherever)
        # TODO: this is sketchy, it's a quick hack. improve - while hopefully we shouldn't need to implement
        # a full spec parser in python :-/
        drop = Box()
        drop.value = False
        for line in lines_upto_prep:
            if line.startswith("%package") or line.startswith("%description"):
                # starts a package or description block for a subpackage; we want to ignore that
                drop.value = True
            else:
                if line.startswith("%") and drop.value is True:
                    # always write that line... we suppose it's an if/endif or a define/global?
                    tempspec.write(line)
                # TODO: any condition that should make us 'undrop' the document?
            if not drop.value:
                tempspec.write(line)

        tempspec.write("%prep\n")
        tempspec.write("cat<<__{}__\n".format(_MY_EOF_MARKER))
        tempspec.writelines(lines_upto_prep)
        tempspec.write("__{}__\n".format(_MY_EOF_MARKER))
        tempspec.close()

        docker = Docker().rm().image(target_image)
        rpmbuild = docker.cmd_and_args("which", "rpmbuild").do_run()
        with_macros = docker.bindmount_dir(tmpdir.path, tmpdir.path).cmd_and_args(rpmbuild, "--nodeps", "-bp",
                                                                                 tempspec_path).do_run()

    return with_macros.split(b"\n")

SOURCE_PATCH_PATTERN = re.compile("^(?:Source|Patch)\d*:\s*((?:http://|https://|ftp://)\S+?)\s*$")

def get_source_and_patches_urls(speclines):
    match_results = (SOURCE_PATCH_PATTERN.match(line) for line in speclines)
    only_matches = (result for result in match_results if result is not None)
    return [result.group(1) for result in only_matches]

def download_files(urls, download_dir):
    wget = pipes.quote(which("wget"))
    download_dir = pipes.quote(download_dir)
    #TODO: think about whether it's better to use URLLib or something like that
    #to download files. We use wget right now because it's easier and has
    #builtin timestamping support.
    joined_urls = " ".join([pipes.quote(url) for url in urls])
    sp("{wget} --directory-prefix={download_dir} --timestamping {joined_urls}", **locals())






















