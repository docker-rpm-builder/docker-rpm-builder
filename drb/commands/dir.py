from __future__ import unicode_literals

import os
import glob
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
from drb.tempdir import TempDir

_HELP = """Builds a binary RPM from a directory. Uses `docker run` under the hood.

    IMAGE should be a docker image id or a repository:tag,
    e.g something like a682b68bbaba or alanfranz/drb-epel-6-x86-64:latest ;
    anything that can be passed to `docker run` as an IMAGE parameter will do.

    SOURCE_DIRECTORY should be a directory containing the .spec or the
    .spectemplate file and all the source files and patches referenced
    in such spec. If using a .spectemplate the directory should be writeable,
    from the host, since a .spec file will be written there (and then removed).
    Such directory will be read-only inside the container.

    TARGET_DIRECTORY is where the RPMS will be written. Anything inside
    may be overwritten during the build phase.

    ADDITIONAL_DOCKER_OPTIONS whatever is passed will be forwarded
    straight to the 'docker run' command. PLEASE REMEMBER to insert a double dash (--)
    before the first additional options, otherwise it will be mistaken
    for a docker-rpm-builder option.

    Options:

    --download-sources: if enabled, SourceX and PatchX from the spec
    that contain an URL will be downloaded from the internet. Such
    files will be placed in SOURCE_DIRECTORY, so it should be writeable.
    Such files won't be deleted afterwards and will be cached for future
    builds.
    WARNING: if this option is used and a file already exists, it may be
    overwritten according to wget --timestamping caching policy.

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
    This option has NO EFFECT when using OSX; Kitematic/docker-machine/boot2docker will always
    set the launching user's permissions on bind-mounted directories.

    --preserve-container: if passed, the build container(s) won't be removed after the build.
    Still, you've got to dig out its id/name yourself. It's useful for debugging purposes,
    by the way.

    --enable-source-overlay: if passed, the source directory - %{_sourcedir} - inside the
    build container will be mounted with an overlay; that will allow the build directory to
    be writeable without propagating modifications to the host, so that it's not necessary to
    rsync/copy the source from the host to the container when compiling.
    WARNING: This runs a PRIVILEGED docker container and requires a 3.18+ kernel with the overlay
             kernel module.

    --verbose: display whatever happens during the build.

    Examples:

    - in this scenario we use no option of ours but we add an option to be forwarded to docker:

    docker-rpm-builder dir a682b68bbaba . /tmp/rpms -- --dns=192.168.1.1

    - in this scenario we use a repository:tag as an image, and we ask drb to download the sources from the internet for us:

    docker-rpm-builder dir alanfranz/drb-epel-6-x86-64:latest /home/user/sourcedir/myproject /tmp/rpms --download-sources

    There's an additional feature which lets you pass further macros to the rpmbuild call inside the container (see
    dockerscripts directory in the source if you want to know more) - if you bind a /rpmmacros file inside the container,
    its content will be copied where it's meant to be used (i.e. ${HOME}/.rpmmacros). Please remember you should use an
    absolute path for the host macros file:

    docker-rpm-builder dir a682b68bbaba . /tmp/rpms -- --volume=/home/user/my.macros:/rpmmacros:ro

    """

_logger = logging.getLogger("drb.commands.dir")

@click.command(help=_HELP)
@click.argument("image", type=click.STRING)
@click.argument("source_directory", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.argument("target_directory", type=click.Path(file_okay=False, resolve_path=True))
@click.argument("additional_docker_options", type=click.STRING, nargs=-1)
@click.option("--download-sources", is_flag=True, default=False)
@click.option("--bash-on-failure", is_flag=True, default=False)
@click.option("--sign-with", nargs=1, type=click.Path(exists=True, dir_okay=False, resolve_path=True), default=None)
@click.option("--always-pull", is_flag=True, default=False)
@click.option("--target-ownership", type=click.STRING, default="{0}:{1}".format(os.getuid(), os.getgid()))
@click.option('--verbose', is_flag=True, default=False)
@click.option('--preserve-container', is_flag=True, default=False)
@click.option('--enable-source-overlay', is_flag=True, default=False)
@click.option('--srpm-target-dir', type=click.Path(exists=True,file_okay=False, resolve_path=True), default=None)
def dir(image, source_directory, target_directory, additional_docker_options, download_sources,
        bash_on_failure, sign_with, always_pull, target_ownership, verbose, preserve_container,
        enable_source_overlay, srpm_target_dir):
    configure_root_logger(verbose)

    docker = Docker().image(image)
    if not preserve_container:
        docker.rm()

    if enable_source_overlay:
        docker.privileged()

    if always_pull:
        _logger.info("Now pulling remote image")
        docker.do_pull(ignore_errors=True)

    with UserExceptionTransformer(Exception, "There must be exactly one spec or spectemplate in source directory."):
        specfile = one([os.path.join(source_directory, fn) for fn in glob.glob1(source_directory, "*.spectemplate")] + \
                [os.path.join(source_directory, fn) for fn in glob.glob1(source_directory, "*.spec")])

    if os.path.splitext(specfile)[1] == ".spectemplate":
        rendered_filename = SpecTemplate.from_path(specfile).render(os.environ)
        specfile = rendered_filename
    specname = os.path.splitext(os.path.basename(specfile))[0] + ".spec"

    if download_sources:
        _logger.info("Now downloading sources")
        with UserExceptionTransformer(Exception, "it was impossible to download at least one source file", append_original_message=True):
            downloadsources(source_directory, specfile, image)

    rpms_inner_dir = docker.cmd_and_args("rpm", "--eval", "%{_rpmdir}").do_run()
    sources_inner_dir = docker.cmd_and_args("rpm", "--eval", "%{_sourcedir}").do_run()
    specs_inner_dir = docker.cmd_and_args("rpm", "--eval", "%{_specdir}").do_run()
    uid, gid = parse_ownership(target_ownership)
    dockerscripts = getpath("drb/dockerscripts")
    if sign_with:
        docker.bindmount_file(sign_with, "/private.key")
    # Map the SRPMs destination directory if needed.
    if srpm_target_dir:
        srpms_inner_dir = docker.cmd_and_args("rpm", "--eval", "%{_srcrpmdir}").do_run()
        docker.bindmount_dir(srpm_target_dir, srpms_inner_dir, read_only=False)
        mkdir_p(srpm_target_dir)
    bashonfail = ""
    if bash_on_failure:
        bashonfail = "bashonfail"
        docker.interactive_and_tty()

    _logger.info("Now building project from %s on image %s", source_directory, image)

    mkdir_p(target_directory)
    with TempDir.platformwise() as tmp:
        docker.additional_options(*additional_docker_options).bindmount_file(specfile, os.path.join(specs_inner_dir, specname)).bindmount_dir(dockerscripts, "/dockerscripts") \
            .bindmount_dir(source_directory, sources_inner_dir).bindmount_dir(target_directory, rpms_inner_dir, read_only=False).workdir("/dockerscripts") \
            .env("ENABLE_SOURCE_OVERLAY", str(int(not enable_source_overlay))).env("CALLING_UID", str(uid)).env("CALLING_GID", str(gid)).env("BASH_ON_FAIL", bashonfail) \
            .cmd_and_args("./rpmbuild-dir-in-docker.sh").bindmount_dir(tmp.path, "/tmp", False)


        with UserExceptionTransformer(Exception, "docker run error", append_original_message=True, final_message="\n\nBuild error. See the log above"):
            if bash_on_failure or verbose:
                docker.do_launch_interactively()
            else:
                docker.do_run()
        _logger.info("Build completed successfully. Your results are in %s", target_directory)










