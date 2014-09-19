# Build native rpm packages through docker.

Why? Because plain rpmbuild may be an hassle (the system may became polluted by cross-project deps, and requires the same native system distro as the target package) and [mock](https://fedoraproject.org/wiki/Projects/Mock) may be slow and sometimes painful to debug and configure.

docker-rpm-builder works on any host distributions that supports [docker](https://www.docker.com/), and is currently tested to build 64 bit Centos 5, 6 and 7 RPM packages.

It's designed to be a very **small and hackable wrapper** to help in rpm building, and lets you build binary RPMs on the fly, without generating a source rpm. I hope to leverage docker capabilities to make the building fast.

[Github homepage](https://github.com/alanfranz/docker-rpm-builder)

## Purpose

My main purpose was to build packages from a CI system, so I wanted to have a directory as the source, not a source rpm which is a unnecessary byproduct. 

This is still a bit annoying (we need a SourceX file) that requires a preprocessing, but I'm working on an auto-packing procedure.

I wanted to be able to build from whatever kind of RPM distribution I wanted, even though I'm especially focused on Redhat/Centos 5, 6 and 7; hence the script supports the base image. You can build your own, use one of mine, or build upon mine.

## Prerequisites

Must have [docker](https://www.docker.com/) installed and properly configured. The user running the build must be able to properly use docker - check your permissions.

You should have a vague idea of what Docker is and how it works, otherwise you might get puzzled.

## Installation

Just 

```git clone https://github.com/alanfranz/docker-rpm-builder.git```

or download the latest [release](https://github.com/alanfranz/docker-rpm-builder/releases/) and unpack somewhere.

There's nothing else to install.

## Building a binary RPM from a directory

The source directory should contain:
* the .spec file
* all the files which are set as **SourceX** and **PatchX** in the spec file (the source directory is something like an uncompressed source rpm);
* optionally, a yum.conf file (will be used while fetching deps and building the rpm in the docker guest - in this situation .repo files will be ignored)
* optionally, any number of .repo files (will be read along yum.conf, only if it wasn't overriden. Default contents of /etc/yum.repos.d are ignored)

## Usage

<pre>
docker-build-binary-rpm-from-dir.sh IMAGETAG SRCDIR [ADDITIONAL_DOCKER_OPTIONS]
</pre>

For building for 64 bit Centos 5-6-7 with EPEL there are some trusted builds on docker hub [here](https://registry.hub.docker.com/u/alanfranz/drb-epel-5-x86-64/), 
[here](https://registry.hub.docker.com/u/alanfranz/drb-epel-6-x86-64/) and [here](https://registry.hub.docker.com/u/alanfranz/drb-epel-7-x86-64/) 

Example for Centos 6:
<pre>
docker-build-binary-rpm-from-dir.sh alanfranz/drb-epel-6-x86-64:latest FULL_PATH_TO_SRC_DIR
</pre>

After build, the output will be in *FULL_PATH_TO_SRC_DIR/RPMS*

Or, using your favourite dns:

<pre>
docker-build-binary-rpm-from-dir.sh alanfranz/drb-epel-6-x86-64:latest FULL_PATH_TO_SRC_DIR --dns=192.168.1.1
</pre>

## Using your own image

You can use whatever base image you like with docker-rpm-builder, as long as it withstands some prerequisites:

- rpmbuild must exist in path
- /docker-rpm-build-root dir must exist in the base image, and hold the traditional *SOURCES,RPMS,SRPMS,SPECS,BUILD* directories.
- yum-builddep must exist in path and accept a .spec file as input
- commands must be able to complete without interaction - consider using a custom yum.conf with *main->assumeyes=1* and be sure all public keys for packages are installed.

Take a look at https://github.com/alanfranz/docker-rpm-builder in order to understand what I mean.

Some of those are subject to change, I'm still thinking about what should I need from my base images.


## Gotchas and TODOS
* if you're used to mock, the build system is a bit different, mocks seems to employ different defaults and has different macros, sometimes a build working with mock may file with docker-rpm-builder. I'm investigating the issue. It's quite uncommon BTW.
* dns default to public ones, will add an option for private ones. Right now you can just add arbitrary docker options after IMAGETAG and SRCDIR
* spec files require source files to be specified; maybe it would be a good idea to create a .tar.gz from the source directory automatically in the host build script.
* use a main drb executable with different targets (see later)
* add target for building a srpm directly
* add target for building from a spectemplate instead of spec, e.g. be able to pass placeholders from outside to our rpm building script.
* document and extend hooks
* Support some way to cache build dependencies between builds for the same package (commit after run? commit after build-dep?)
* Support some way of forcing remote image tag update before building.
* Option for drop into interactive shell if build fails


