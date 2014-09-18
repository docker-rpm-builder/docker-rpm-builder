# Build rpms through docker.

Why? Because plain rpmbuild may be an hassle (the system may became polluted by cross-project deps, and requires the same native system distro as the target package) and [mock](https://fedoraproject.org/wiki/Projects/Mock) may be slow and sometimes painful to debug and configure.

docker-rpm-builder works on any host distributions that supports [docker](https://www.docker.com/).

It's designed to be a very **small and hackable wrapper** to help in rpm building, and lets you build binary RPMs on the fly, without generating a source rpm. I hope to leverage docker capabilities to make the building fast.


## Prerequisites

Must have [docker](https://www.docker.com/) installed and properly configured. The user running the build must be able to properly use docker - check your permissions.

## Building a binary RPM from a directory

The directory should contain:
* the .spec file
* all files which are marked as **SourceX** and **PatchX** in the spec file (the source is something like an uncompressed source rpm);
* optionally, a yum.conf file (will be used while fetching deps and building the rpm in the docker guest - in this situation .repo files will be ignored)
* optionally, any number of .repo files (will be placed in /etc/yum.repos.d of the docker guest)

### Usage

<pre>
docker-build-binary-rpm-from-dir.sh IMAGETAG SRCDIR [ADDITIONAL_DOCKER_OPTIONS]
</pre>

For building for Centos 6 with EPEL enabled there's a trusted build on docker hub [here](https://registry.hub.docker.com/u/alanfranz/drb-epel-6-x86-64/) ([github source](https://github.com/alanfranz/docker-rpm-builder-configurations))

<pre>
docker-build-binary-rpm-from-dir.sh alanfranz/drb-epel-6-x86-64:latest FULL_PATH_TO_SRC_DIR
</pre>

Using your favourite dns:

<pre>
docker-build-binary-rpm-from-dir.sh alanfranz/drb-epel-6-x86-64:latest FULL_PATH_TO_SRC_DIR --dns=192.168.1.1
</pre>

## Gotchas and TODOS
* if you're used to mock, the build system is a bit different, mocks seems to employ different defaults and has different macros, sometimes a build working with mock may file with docker-rpm-builder. I'm investigating the issue.
* dns default to public ones, will add an option for private ones. Right now you can just add arbitrary docker options after IMAGETAG and SRCDIR
* spec files require source files to be specified; maybe it would be a good idea to create a .tar.gz from the source directory automatically in the host build script.
* use a main drb executable with different targets (see later)
* add target for building a srpm directly
* add target for building from a spectemplate instead of spec


