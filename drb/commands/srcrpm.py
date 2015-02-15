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
from drb.bash import serialize, provide_encoded_signature, spawn_interactive

_HELP = """Builds a binary RPM from .src.rpm file.
    Uses `docker run` under the hood.

    IMAGE should be a docker image id or a repository:tag,
    e.g something like a682b68bbaba or alanfranz/drb-epel-6-x86-64:latest ;
    anything that can be passed to `docker run` as an IMAGE parameter will do.

    SRCRPM should be a .src.rpm file that contains the .spec and all the
    references source files.

    TARGET_DIRECTORY is where the RPMS will be written. Anything inside
    may be overwritten during the build phase.

    ADDITIONAL_DOCKER_OPTIONS whatever is passed will be forwarded
    straight to the 'docker run' command. PLEASE REMEMBER to insert a double dash (--)
    before the first additional option, otherwise it will be mistaken
    for a docker-rpm-builder option.

    Options:

    --verify-signature: if enabled, the .src.rpm signature will be verified;
    if the verification fails, the build will be aborted.

    --bash-on-failure: if enabled, the tool will drop in an interactive
    shell inside the container if the build fails.

    --sign-with <PATH>: if passed, the chosen GPG key file is used to sign the package.
    Currently, such file MUST be a readable, password-free, ascii-armored
    GPG private key file.

    --always-pull: if passed, a `docker pull` for the latest
    image version from Docker Hub (or other configured endpoint) is performed. Please note that
    any error that may arise from the operation is currently ignored.

    Examples:

    - in this scenario we use no option of ours but we add an option to be forwarded to docker:

    docker-rpm-builder srcrpm a682b68bbaba mypackage.src.rpm /tmp/rpms -- --dns=192.168.1.1

    - in this scenario we use a repository:tag as an image, and we ask drb to sign the package

    docker-rpm-builder srcrpm alanfranz/drb-epel-6-x86-64:latest mypackage.src.rpm /tmp/rpms --sign-with mykey.pgp
    """

_logger = logging.getLogger("drb.commands.srcrpm")

@click.command(help=_HELP)
@click.argument("image", type=click.STRING)
@click.argument("srcrpm", type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument("target_directory", type=click.Path(file_okay=False, resolve_path=True))
@click.argument("additional_docker_options", type=click.STRING, nargs=-1)
@click.option("--verify-signature", is_flag=True)
@click.option("--bash-on-failure", is_flag=True)
@click.option("--sign-with", nargs=1, type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.option("--always-pull", is_flag=True)
def srcrpm(image, srcrpm, target_directory, additional_docker_options, verify_signature=False, bash_on_failure=False,
           sign_with=None, always_pull=False):
    _logger.info("Now building %(srcrpm)s on image %(image)s", locals())
    if not os.path.exists(target_directory):
        os.mkdir(target_directory)

    dockerexec = which("docker")
    dockerscripts = getpath("drb/dockerscripts")
    srpms_temp = tempfile.mkdtemp("SRPMS")
    shutil.copy(srcrpm, srpms_temp)
    internal_docker_options = set()
    srcrpm_basename = os.path.basename(srcrpm)
    uid = os.getuid()
    gid = os.getgid()
    rpmbuild_options = "" if verify_signature else "--nosignature"

    bashonfail = ""
    spawn_func = sp
    if bash_on_failure:
        internal_docker_options.add("-i")
        internal_docker_options.add("-t")
        bashonfail = "bashonfail"
        spawn_func = spawn_interactive

    internal_docker_options = " ".join(internal_docker_options)
    encoded_signature = provide_encoded_signature(sign_with)

    if always_pull:
        pull(dockerexec, image)

    serialized_options = serialize({"CALLING_UID": uid, "CALLING_GID": gid, "BASH_ON_FAIL":bashonfail, "RPMBUILD_OPTIONS": rpmbuild_options, "SRCRPM": srcrpm_basename,
                                    "GPG_PRIVATE_KEY": encoded_signature})

    try:
        additional_docker_options = internal_docker_options + " ".join(additional_docker_options)
        srpms_inner_dir = sp("{dockerexec} run --rm {image} rpm --eval %{{_srcrpmdir}}", **locals()).strip()
        rpms_inner_dir = sp("{dockerexec} run --rm {image} rpm --eval %{{_rpmdir}}", **locals()).strip()
        spawn_func("{dockerexec} run {additional_docker_options} -v {dockerscripts}:/dockerscripts -v {srpms_temp}:{srpms_inner_dir} -v {target_directory}:{rpms_inner_dir}"
           " -w /dockerscripts {image} ./rpmbuild-srcrpm-in-docker.sh {serialized_options}", **locals())
    finally:
        shutil.rmtree(srpms_temp)

