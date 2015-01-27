# Build native rpm packages through docker.

**Heavy work in progress, some information may be outdated or not up-to-date yet**

Why? Because plain rpmbuild may be an hassle (the system may became polluted by cross-project deps, and requires the same native system distro as the target package) and [mock](https://fedoraproject.org/wiki/Projects/Mock) may be slow and sometimes painful to debug and configure.

docker-rpm-builder works on any host distributions that supports [docker](https://www.docker.com/), and is currently tested to build 64 bit Centos 5, 6 and 7 RPM packages, as well as Fedora 20, 21 and rawhide.

It's designed to be a very **small and hackable wrapper** to help in rpm building, and lets you build binary RPMs on the fly, **without generating an intermediate source rpm**, which is a bit of an unnecessary byproduct nowadays, since most source tracking is done in a revision control system. Docker capabilities are leveraged to make the build **fast**; copy is limited, and bind-mount between host and container is privileged whenever it's possible.

This is **not** a different build system like [fpm](https://github.com/jordansissel/fpm), which has its own options and wraps different distributions' build tools; it requires normal rpm building capabilities capabilities, but improves on the "standard workflow"

[Github homepage](https://github.com/alanfranz/docker-rpm-builder)

## Purpose

- let an rpm be properly built on any host distribution, including non-RPM ones;
- let an rpm be built without polluting the source distribution with unneeded, build-only packages;
- make rpm building fast;
- make rpm building continuous integration friendly;
- make rpm building debuggable, by letting the user spawn an interactive shell on the fly whenever a build error happens;


## Prerequisites

Must have [docker](https://www.docker.com/) installed and properly configured (see the [install docs](https://docs.docker.com/installation/#installation). The user running the build must be able to properly use docker - check your permissions.

You should have a vague idea of what Docker is and how it works, otherwise you might get puzzled.

Python 2.7, Bash and perl should be installed on your system as well.

## Installation

docker-rpm-builder is a pure-python, self-contained python package.

You could install it in your system straight with [pip](https://pypi.python.org/pypi/pip), but I actually recommend [pipsi](https://pypi.python.org/pypi/pipsi), which will automatically creates an isolated environment for your python packages and requires no additional privileges; everything is done with non-root privileges.

So, install pipsi if you don't have it, making sure the **python** interpreter you're using is 2.7:

```
curl https://raw.githubusercontent.com/mitsuhiko/pipsi/master/get-pipsi.py | python
```

then

```
pipsi install docker-rpm-builder
```

to upgrade docker-rpm-builder to the latest version, use:

```
pipsi upgrade docker-rpm-builder
```


## Building a binary RPM straight from a directory

You should have a source directory that contains:
* either a .spec file or a [.spectemplate](#spectemplates) file
* any file that is set as **SourceX** and **PatchX** in the spec file (
if any of your SourceX or PatchX files are URLs, you can use the --download-sources option if the files are not already there.)

Then, you should pass a source directory, which will be bound to %{_sourcedir} inside the build container (e.g. /root/rpmbuild/SOURCES on RHEL7 or ). You can access such directory straight from your specfile. If you pass --download-sources the URL sources will be downloaded in such directory, so be sure to set the proper ignores for it in your revision control system.

Of course, you should tell the tool which build image you'd like to use. I've baked some [prebuilt images](#prebuilt-images), but you should feel free to create your own, since that's the purpose of this tool.

And you should tell the tool which target directory you'd like to use for rpm output; this directory whill be bound straight to %{_rpmdir} inside the build container, so mind that if your build process does something strange with it, files can be deleted. If the target directory doesn't exist it will be created.

### Example

```
docker-rpm-builder dir --download-sources alanfranz/drb-epel-5-x86-64:latest . /tmp/rpms
```

This command will build straight from current dir with the alanfranz/drb-epel-5-x86-64:latest image and output the RPMs you requested in /tmp/rpms.

There're further options to explore: just type

```
docker-rpm-builder dir --help
```

To see everything.

URL-based source/patch downloading, shell spawning on build failure, signing, and always pulling the remote images are all supported scenarios.


### Spectemplates

The spectemplate approach prevents you from editing the .spec file (or creating a new one) for each build; inside your .spectemplate, just define
substitution tags, which are names between @s, e.g.

```
@BUILD_NUMBER@
```

If there's an environment variable called BUILD_NUMBER when you build your project, such variable will be substituted straight into your spec. This is especially useful in an CI server which builds your packages. Consider the .spectemplate for this very project, [docker-rpm-builder.spectemplate](docker-rpm-builder.spectemplate) , and you can see the @BUILD_NUMBER@ and @GIT_COMMIT@ substitution variables at work; those are set by the [Jenkins][http://jenkins-ci.org/] build server.

Please note: you can't have both a .spec and a .spectemplate in your source directory. That will cause an error.

## Rebuilding a source RPM

Rebuilding a .src.rpm file is supported as well. Just check the command:

```
docker-rpm-builder srcrpm --help
```

## Build images

Build images are nothing esoteric. They're just plain OS images with a set of packages, settings and maybe some macros which are needed to perform a build and/or to sign packages. See the [next section](#prebuilt-images) for some examples.

In order to use an image for building an RPM:

- rpmbuild must exist in path
- yum-builddep must exist in path and accept a .spec file or a .src.rpm as input
- commands must be able to complete without interaction - consider using a custom yum.conf with *main->assumeyes=1* and be sure all public keys for your repositories are installed.
- if you want to sign packages, make sure you install **gnupg** 1.4 and set a proper **%__gpg_sign_cmd** macro in */etc/rpm*

### Prebuilt images

There're some prebuilt configurations for Centos 5-6-7+EPEL and Fedora 20-21-rawhide at [https://github.com/alanfranz/docker-rpm-builder-configurations](); those are available on [my docker hub page](https://hub.docker.com/u/alanfranz/) as well, so they can be used immediately out of the box. The following are all valid build images:

- alanfranz/drb-epel-5-x86-64:latest
- alanfranz/drb-epel-6-x86-64:latest
- alanfranz/drb-epel-7-x86-64:latest
- alanfranz/drb-fedora-20-x86-64:latest
- alanfranz/drb-fedora-21-x86-64:latest
- alanfranz/drb-fedora-rawhide-x86-64:latest

## Speedup your build: image reuse

The impact of this change can be great if you're building a small package with a certain frequency.

In such situation, the dependency download time can just waste any speed that you could gain by using this tool.

So what?

Well, just use an image which pre-caches your build dependencies!

create a directory like *build-image* in your project directory, and enter something like this:

```
FROM alanfranz/drb-epel-6-x86-64:latest
MAINTAINER myself myself@example.com
RUN yum install openssl openssl-devel
```

in your makefile/buildscript/whatever, do something like:

```
pushd build-image
docker build -t myprojectbuildimage .
popd

docker-rpm-builder dir myprojectbuildimage . rpm_output
```

docker is smart enough to *not* rebuild an image which is unchanged since last build,
hence executing the docker build multiple times will take no time at all unless
you change your Dockerfile.

And since you've already added all build prerequisites, no download will happen.

In the future I may think about adding an option to docker-rpm-builder to help creating
such images without actually needing a Dockerfile on a source repo.

## Gotchas
* if you're used to mock, the build system is a bit different, mocks seems to employ different defaults and has different macros, sometimes a build working with mock may file with docker-rpm-builder. I'm investigating the issue. It's quite uncommon BTW.
* dns default to public ones, will add an option for private ones. Right now you can just add arbitrary docker options after IMAGETAG and SRCDIR

## TODOS and ideas
* Support some way to cache build dependencies between builds for the same package (commit after run? commit after build-dep?)
* Smoke tests to see whether everything is properly built
* Better RPM package
* DEB package
