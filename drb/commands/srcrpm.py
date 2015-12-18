# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import shutil
import logging
import click

from drb.configure_logging import configure_root_logger
from drb.docker import Docker
from drb.mkdir_p import mkdir_p
from drb.tempdir import TempDir
from drb.path import getpath
from drb.parse_ownership import parse_ownership

_HELP = """Builds a binary RPM from .src.rpm file.
    Uses `docker run` under the hood.

    IMAGE should be a docker image id or a repository:tag,
    e.g something like a682b68bbaba or alanfranz/drb-epel-6-x86-64:latest ;
    anything that can be passed to `docker run` as an IMAGE parameter will do.

    SRCRPM should be a .src.rpm file that contains the .spec and all the
    references source files. It will be readonly inside the container.

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

    --target-ownership: a string in NN:MM format, which let you choose the ownership of the files
    in the output directory. Defaults to current user's uid:gid if not passed. Must be numeric.
    Not supported on OSX.

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
@click.option("--verify-signature", is_flag=True, default=False)
@click.option("--bash-on-failure", is_flag=True, default=False)
@click.option("--sign-with", nargs=1, type=click.Path(exists=True, dir_okay=False, resolve_path=True), default=None)
@click.option("--always-pull", is_flag=True, default=False)
@click.option("--target-ownership", type=click.STRING, default="{0}:{1}".format(os.getuid(), os.getgid()))
@click.option('--verbose', is_flag=True, default=False)
def srcrpm(image, srcrpm, target_directory, additional_docker_options, verify_signature, bash_on_failure,
           sign_with, always_pull, target_ownership, verbose):
    configure_root_logger(verbose)

    docker = Docker().rm().image(image)

    if always_pull:
        _logger.info("Now pulling remote image")
        docker.pull(ignore_errors=True)

    srpms_inner_dir = docker.cmd_and_args("rpm", "--eval", "%{_srcrpmdir}").run()
    rpms_inner_dir = docker.cmd_and_args("rpm", "--eval", "%{_rpmdir}").run()
    uid, gid = parse_ownership(target_ownership)
    rpmbuild_options = "" if verify_signature else "--nosignature"
    dockerscripts = getpath("drb/dockerscripts")
    bashonfail = "bashonfail" if bash_on_failure else ""
    docker.additional_options(*additional_docker_options)
    if sign_with:
        docker.bindmount_file(sign_with, "/private.key")

    with TempDir.platformwise() as srpms_temp:
        shutil.copy(srcrpm, srpms_temp.path)
        srcrpm_basename = os.path.basename(srcrpm)
        mkdir_p(target_directory)
        docker.bindmount_dir(dockerscripts, "/dockerscripts").bindmount_dir(srpms_temp.path, srpms_inner_dir) \
            .bindmount_dir(target_directory, rpms_inner_dir, read_only=False).workdir("/dockerscripts") \
            .env("CALLING_UID", str(uid)).env("CALLING_GID", str(gid)).env("BASH_ON_FAIL", bashonfail) \
            .env("RPMBUILD_OPTIONS", rpmbuild_options).env("SRCRPM", srcrpm_basename) \
            .cmd_and_args("./rpmbuild-srcrpm-in-docker.sh")
        _logger.info("Now building %(srcrpm)s on image %(image)s", locals())

        if bash_on_failure:
            docker.run_interactive()
        else:
            docker.run()
