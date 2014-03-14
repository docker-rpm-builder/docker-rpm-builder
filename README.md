# Build rpms through docker.

Why? Because plain rpmbuild may be an hassle (the system may became polluted by cross-project deps, and requires the same native system distro as the target package) and [mock](https://fedoraproject.org/wiki/Projects/Mock) may be slow and sometimes painful to debug and configure.

## Prerequisites

Must have [docker](https://www.docker.io/) installed and properly configured. The user running the build must be able to properly use docker.

## Building a binary RPM from a directory

The directory should contain:
* the .spec file
* all files which are marked as **SourceX** in the spec file;
* optionally, a yum.conf file (will be used while fetching deps and building the rpm in the docker guest)
* optionally, any number of .repo files (will be placed in /etc/yum.repos.d of the docker guest)

### Usage

<pre>
docker-build-binary-rpm-from-dir.sh IMAGETAG SRCDIR
</pre>

For building for Centos 6 with EPEL enabled there's a trusted build [here](https://index.docker.io/u/alanfranz/drb-epel-6-x86-64/) ([github source](https://github.com/alanfranz/docker-rpm-builder-configurations))

<pre>
docker-build-binary-rpm-from-dir.sh alanfranz/drb-epel-6-x86-64 FULL_PATH_TO_SRC_DIR
</pre>

the SRC_DIR should contain:

## Gotchas and TODOS
* if you're used to mock, the build system is a bit different, mocks seems to employ different defaults and has different macros, sometimes a build working with mock may file with docker-rpm-builder. I'm investigating the issue.
* dns default to public ones, will add an option for private ones.
* spec files require source files to be specified; maybe it would be a good idea to create a .tar.gz from the source directory automatically in the host build script, this is 


