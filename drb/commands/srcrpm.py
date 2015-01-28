# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import shutil
import logging
import tempfile
import click

from drb.which import which
from drb.spawn import sp
from drb.path import getpath
from drb.pull import pull
from drb.bash import serialize, provide_encoded_signature

_HELP = """Builds a binary RPM from .src.rpm file.
    Uses `docker run` under the hood.
    """

_logger = logging.getLogger("drb.commands.srcrpm")

@click.command(help=_HELP)
@click.argument("image", type=click.STRING)
@click.argument("srcrpm", type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument("target_directory", type=click.Path(file_okay=False, resolve_path=True))
@click.option("--verify-signature", is_flag=True)
@click.option("--bash-on-failure", is_flag=True)
@click.option("--sign-with", nargs=1, type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.option("--always-pull", is_flag=True)
def srcrpm(image, srcrpm, target_directory, verify_signature=False, bash_on_failure=False,
           sign_with=None, always_pull=False):
    _logger.info("Now building %(srcrpm)s on image %(image)s", locals())
    if not os.path.exists(target_directory):
        os.mkdir(target_directory)

    dockerexec = which("docker")
    dockerscripts = getpath("drb/dockerscripts")
    srpms_temp = tempfile.mkdtemp("SRPMS")
    shutil.copy(srcrpm, srpms_temp)
    additional_docker_options = set()
    srcrpm_basename = os.path.basename(srcrpm)
    uid = os.getuid()
    gid = os.getgid()
    rpmbuild_options = "" if verify_signature else "--nosignature"

    bashonfail = ""
    if bash_on_failure:
        additional_docker_options.add("-i")
        additional_docker_options.add("-t")
        bashonfail = "bashonfail"

    additional_docker_options = " ".join(additional_docker_options)
    encoded_signature = provide_encoded_signature(sign_with)

    if always_pull:
        pull(dockerexec, image)

    serialized_options = serialize({"CALLING_UID": uid, "CALLING_GID": gid, "BASH_ON_FAIL":bashonfail, "RPMBUILD_OPTIONS": rpmbuild_options, "SRCRPM": srcrpm_basename,
                                    "GPG_PRIVATE_KEY": encoded_signature})

    try:
        srpms_inner_dir = sp("{dockerexec} run {image} rpm --eval %{{_srcrpmdir}}", **locals()).strip()
        rpms_inner_dir = sp("{dockerexec} run {image} rpm --eval %{{_rpmdir}}", **locals()).strip()
        sp("{dockerexec} run {additional_docker_options} -v {dockerscripts}:/dockerscripts -v {srpms_temp}:{srpms_inner_dir} -v {target_directory}:{rpms_inner_dir}"
           " -w /dockerscripts {image} ./rpmbuild-srcrpm-in-docker.sh {serialized_options} {additional_docker_options}", **locals())
    finally:
        shutil.rmtree(srpms_temp)

