# Build rpms through docker.

Why? Because plain rpmbuild may be an hassle (the system may became polluted by cross-project deps, and requires the same native system distro as the target package) and [mock](https://fedoraproject.org/wiki/Projects/Mock) may be slow and sometimes painful to debug and configure.

docker-rpm-builder works on any host distributions that supports docker.

It's designed to be a very small and hackable wrapper to help in rpm building, and lets you building binary RPMs on the fly, without generating a source rpm. I hope to leverage docker capibilities to make the building fast.


## Prerequisites

Must have [docker](https://www.docker.io/) installed and properly configured. The user running the build must be able to properly use docker.

Then you have to create a Docker image that will be reused for each build.

<pre>
git clone https://github.com/alanfranz/docker-rpm-builder.git
cd docker-rpm-builder
docker build -t docker-rpm-builder .
</pre>


## Building a binary RPM from a directory

The directory should contain:
* the .spec file
* all local files which are marked as **SourceX** or **PatchX** in the spec file;
* optionally, a yum.conf file (will be used while fetching deps and building the rpm in the docker guest)
* optionally, any number of .repo files (will be placed in /etc/yum.repos.d of the docker guest)

### Usage

<pre>
docker-build-binary-rpm-from-dir.sh docker-rpm-builder FULL_PATH_TO_SRC_DIR [ADDITIONAL_DOCKER_OPTIONS]
</pre>

For building for Centos 6 with EPEL enabled there's a trusted build [here](https://index.docker.io/u/alanfranz/drb-epel-6-x86-64/) ([github source](https://github.com/alanfranz/docker-rpm-builder-configurations))

<pre>
docker-build-binary-rpm-from-dir.sh alanfranz/drb-epel-6-x86-64 FULL_PATH_TO_SRC_DIR
</pre>

## Gotchas and TODOS
* if you're used to mock, the build system is a bit different, mocks seems to employ different defaults and has different macros, sometimes a build working with mock may file with docker-rpm-builder. I'm investigating the issue.
* dns default to public ones, will add an option for private ones. Right now you can just add arbitrary docker options after IMAGETAG and SRCDIR
* spec files require source files to be specified; maybe it would be a good idea to create a .tar.gz from the source directory automatically in the host build script, this is 


