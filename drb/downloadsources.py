# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
from tempfile import NamedTemporaryFile
import codecs
from itertools import takewhile
from drb.spawn import sp
from drb.which import which
from drb.path import getpath
import re

_logger = logging.getLogger("drb.downloadsources")

def downloadsources(source_directory, specfilename):
    """Leverages rpmbuild to complete the macros in a spec file, then
    uses wget to fetch source and patch files."""
    _logger.info("Downloading additional sources")

    lines = get_spec_with_resolved_macros(specfilename)
    urls = get_source_and_patches_urls(lines)
    download_files(urls, source_directory)

def get_spec_with_resolved_macros(specfilename):
    lines_upto_prep =list(takewhile(lambda line: not line.startswith("%prep"),
                                    codecs.open(specfilename, encoding="utf-8")))

    tempspec = NamedTemporaryFile(suffix=".spec")
    tempspec.writelines(lines_upto_prep)
    tempspec.write("%prep\n")
    tempspec.write("cat<<__EOF__\n")
    tempspec.writelines(lines_upto_prep)
    tempspec.write("__EOF__\n")
    tempspec.flush()

    try:
        rpmbuild = which("rpmbuild")
        with_macros = sp("{rpmbuild} --nodeps -bp {tempspec.name}", **locals())
    finally:
        tempspec.close()

    return with_macros.split("\n")

SOURCE_PATCH_PATTERN = re.compile("^(?:Source|Patch)\d*:\s*((?:http://|https://|ftp://)\S+?)\s*$")

def get_source_and_patches_urls(speclines):
    match_results = (SOURCE_PATCH_PATTERN.match(line) for line in speclines)
    only_matches = (result for result in match_results if result is not None)
    return [result.group(1) for result in only_matches]

def download_files(urls, download_dir):
    wget = which("wget")
    #TODO: think about URL sanitization.
    #TODO: think about whether it's better to use URLLib or something like that
    #to download files. We use wget right now because it's easier and has
    #builtin timestamping support.
    joined_urls = " ".join(urls)
    sp("{wget} --directory-prefix={download_dir} --timestamping {joined_urls}", **locals())






















