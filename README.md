# Fast native RPM building from any distro, for any distro, via docker.

## News

See the [News Page](https://github.com/alanfranz/docker-rpm-builder/wiki/News) for the latest news.

See also [FPM within Docker](https://github.com/alanfranz/fpm-within-docker) - an alternative way of building RPMs and DEBs
that could make things even easier for you.

## For whom is this software designed?

If you already know a bit about RPM packaging, and you're quite confident reading or writing a specfile, either because you need to (e.g. you've got a package that needs very fine tuning) or
because you must (e.g. you need your package to work in existing distributions' workflows where a .src.rpm and a specfile are required).

If you just need to package your software in an RPM and don't care too much about conventions, fine tuning, ecc, take a look at [FPM within Docker](https://github.com/alanfranz/fpm-within-docker). It'll
make your life easier without much fuss.

## Why?

If you think using plain [rpmbuild](http://www.rpm.org/max-rpm-snapshot/ch-rpm-b-command.html) is painful because it requires you to setup a server/vm with the same OS as the build target
and then transfer your development code, and you don't like [mock](https://fedoraproject.org/wiki/Projects/Mock) because a) it's a complex piece of software that makes debugging failed builds a bit hard,
b) sometimes produces errors which are not so easy to understand without digging into its source code, and c) is very hard to run on non-RHEL/Centos/Fedora host distros, then you're in the right place.

Basically, docker-rpm-builder is an ecosystem comprising a way to run rpmbuild inside docker-based containers. Both the tool and a basic set of target build images is included.

## Key features

* Works on any host distribution that supports docker.
* It's very small and hackable. Take a look at the source code: making modifications is trivial.
* Can build straight from the source directory **without an intermediate .src.rpm**
* It supports a basic templating system for specfiles, which is especially useful in CI contexts.
* It lets you spawn an interactive shell if the build fails, **in the very place where it fails**
* If you use a precise build image and hold all build dependencies within, your builds will be highly reproducible.
* Cache build dependencies; don't re-download unless your spec changes.
* The root filesystem is fully writable, letting you install to the 'real' target directory and moving to $RPM_BUILD_ROOT at the end of the build - that's very useful for compiled software that doesn't
  support PREFIX and after-install relocation properly. Such writes are not persisted within the build image,

## Limitations

* Currently limited to x86_64 for both host and target. That's a docker limitation which is unlikely to go away soon. 32 bit container images for Docker do exist, but they're considered unsupported by this tool.

## Required knowledge

You should have a vague idea of what [docker](https://www.docker.com) is and you should already know how to build an RPM - see to [Maximum RPM](http://www.rpm.org/max-rpm/) and other documentation from Fedora [HowTO](https://fedoraproject.org/wiki/How_to_create_an_RPM_package) [RPM Guide](http://docs.fedoraproject.org/en-US/Fedora_Draft_Documentation/0.1/html/RPM_Guide/).

## Prerequisites

At the dawn of this tool, I tried to make it work with any version of *docker* that would come from the distributions' repository or from official repository. This proved to be quite troublesome, and the docker environment is advancing rapidly; it makes no sense to use or support older versions of *docker*.

So, **docker >= 1.10** is currently a prerequisite. If you're using the prebuilt RPMs or DEBs, they expect the **docker-engine** package from yum.dockerproject.org or apt.dockerproject.org to be available; just follow the [official install instructions](https://docs.docker.com/engine/installation/).

This tool is designed to use a docker-engine on the very same machine where it's running, not a remote docker daemon. On OSX, it uses docker-machine, but make sure all the files
you're using reside in ```/Users```.

Python 2.7, bash, and wget should be installed on your system as well. If you're using a packaged version, the package will take care of that.

See the section below for details on some post-install actions for docker.

### Docker configuration

If docker is already up and running on your system, you probably need to do absolutely nothing else.

Otherwise, if it's your first time with docker, here's a checklist:

* Verify the *docker* service is running
* Verify the *docker* group exists and your user belongs to it. It is advised **not to run docker-rpm-builder as root**. The docker package on some recent Fedoras seems to add a *dockerroot* group instead - **it won't do!**
* If you had to add the group, verify you've restarted the *docker* service after such addition
* Verify you've logged out+in after adding your user to the group
* Verify selinux is disabled. There seems to be work going on to let docker work along selinux, but I could not succeed at using bindmounts as long as selinux is active.
* Verify your disk has enough free space


## Installation

### CentOS 7.x / RHEL 7.x

CentOS 6 / RHEL 6 support for docker-rpm-builder has been discontinued along docker's own support. I'm sorry. If you really need to use such distros, you can try the source install described below, along with docker 1.7.

There's an RPM repository for those distributions - such packages are built via docker-rpm-builder itself. Just use this yum repository:

**/etc/yum.repos.d/docker-rpm-builder-v1.repo**
```
[docker-rpm-builder-v1]
name=docker-rpm-builder-v1
baseurl=http://www.a9f.eu/yum/docker-rpm-builder-v1/centos/$releasever/$basearch
repo_gpgcheck=1
gpgcheck=1
enabled=1
gpgkey=https://www.franzoni.eu/keys/D1270819.txt
```

Such repo should work properly for Centos, RHEL and Oracle Linux. Scientific Linux insists, AFAIK, un using sub-releases on $releasever, you should substitute your major to $releasever in the above URL if you're using SL.

Please refer to docker's own installation instructions for [CentOS](https://docs.docker.com/installation/centos/) and [RHEL](https://docs.docker.com/installation/rhel/) for details. You'll probably need to enable [EPEL](https://fedoraproject.org/wiki/EPEL) or distro-specific extras repositories for the install to succeed.

docker-rpm-builder already depends on the proper docker package for each distribution; once your repos are in place, just

```
yum install docker-rpm-builder
```

And you're done; if you haven't already done so, check the [docker configuration](#docker-configuration) section, then [launch the test suite](#test-everything-works)

#### Support plan

I plan to support the latest CentOS/RHEL stable.

### Fedora 23

Use this yum repository:

**/etc/yum.repos.d/docker-rpm-builder-v1.repo**
```
[docker-rpm-builder-v1]
name=docker-rpm-builder-v1
baseurl=http://www.a9f.eu/yum/docker-rpm-builder-v1/fedora/$releasever/$basearch
repo_gpgcheck=1
gpgcheck=1
enabled=1
gpgkey=https://www.franzoni.eu/keys/D1270819.txt
```

Please refer to docker installation instructions for [Fedora](https://docs.docker.com/installation/fedora/) for details.

docker-rpm-builder already depends on the proper docker package for each distribution; once your repos are in place, just

```
yum install docker-rpm-builder
```

And you're done; if you haven't already done so, check the [docker configuration](#docker-configuration) section, then [launch the test suite](#test-everything-works)

#### Support plan

I'll probably always support the latest released Fedora distribution. When a new Fedora is released,
I'll try supporting the new release as well as the old one for a couple of months, then drop the old one.

Example (January 2016). There's a package for Fedora 23. Fedora 24 is planned for June 2016. Once it's out, I'll create a new package
for Fedora 24. Around September 2016, any support for Fedora 23 will be dropped.


### Debian Jessie

This is a supported distro; you'll need to enable the official docker package from docker.io [see install docs](https://docs.docker.com/installation/) or docker-rpm-builder will fail to install.

First, you should make sure that you've got my package signing key properly installed and configured for apt:
```
curl https://www.franzoni.eu/keys/D1270819.txt | sudo apt-key add -
```

Then, pick the repo for your distribution - see below - and save it as **/etc/apt/sources.list.d/docker-rpm-builder.list**

```
deb http://www.a9f.eu/apt/docker-rpm-builder-v1/debian jessie main
```

Now you're ready to

```
apt-get update
apt-get -y install docker-rpm-builder
```

And you're done; if you haven't already done so, check the [docker configuration](#docker-configuration) section, then [launch the test suite](#test-everything-works)

#### Support plan

I plan to support the latest stable Debian release. When a new release comes out,
I'll support the oldstable for a few months before dropping it.


### Ubuntu

There're repositories for those distributions; you'll need to enable the official docker package from docker.io [see install docs](https://docs.docker.com/installation/) or docker-rpm-builder will fail to install.

First, you should make sure that you've got my package signing key properly installed and configured for apt:
```
curl https://www.franzoni.eu/keys/D1270819.txt | sudo apt-key add -
```

Then, pick the repo for your distribution - see below - and save it as **/etc/apt/sources.list.d/docker-rpm-builder.list**

**Trusty**

```
deb http://www.a9f.eu/apt/docker-rpm-builder-v1/ubuntu trusty main
```

**Wily**

```
deb http://www.a9f.eu/apt/docker-rpm-builder-v1/ubuntu wily main
```

Now you're ready to

```
apt-get update
apt-get -y install docker-rpm-builder
```

And you're done; if you haven't already done so, check the [docker configuration](#docker-configuration) section, then [launch the test suite](#test-everything-works)

#### Support plan

I plan to support the latest Ubuntu LTS as well as the latest-and-greatest Ubuntu release.
Whenever a new version comes out there'll be probably be some months of overlapping support,
and I'll probably choose to support older LTSes for more time than "standard" releases
(e.g. I don't plan dropping Ubuntu 14.04 support for the whole 2016, even though 16.04 is
scheduled for April 2016)


### Other distributions and OSX - installing straight from source

* Check the [prerequisites](#prerequisites) and the [docker configuration](#docker-configuration) sections.
* make sure you've got ```python 2.7``` and ```virtualenv``` available on your system.
* make sure you've got ```wget```.
* clone this repository. Pick the ```v1``` branch, which is where I keep stable releases.
* run ```make```.  You can pass the VIRTUALENV variable to tell make which virtualenv executable to use (e.g ```make VIRTUALENV='virtualenv -p /usr/bin/python2.7'```)
* ```devenv/bin/docker-rpm-builder``` will contain the docker-rpm-builder executable.
* Run the integrated test suite; see next section.

## Test everything works!

docker-rpm-builder features an integrated test suite. Run:

```
docker-rpm-builder selftest
```

It requires an Internet connection and may take a bit of time for the first run, since it will be downloading a minimal image.

If you want to be extra-sure everything is fine, run:

```
docker-rpm-builder selftest --full
```

It will take a really long time to run, especially on your first time.

## Usage

## Building a binary RPM straight from a directory

You should have a source directory that contains:
* either a .spec file or a [.spectemplate](#spectemplates) file
* any file that is set as **SourceX** and **PatchX** in the spec file (
if any of your SourceX or PatchX files are URLs, you can use the --download-sources option if the files are not already there.)

Then, you should pass a source directory, which will be bind-mounted straight to %{_sourcedir} inside the build container (e.g. /root/rpmbuild/SOURCES on RHEL7 ). You can access such directory straight from your specfile. **The source directory is mounted read-only** to prevent accidental modifications during the build phase.

If you pass --download-sources the URL sources will be downloaded in such directory, so be sure to set the proper ignores for it in your revision control system.

Of course, you should tell the tool which build image you'd like to use; that's the image where the build will happen. I've baked some [prebuilt images](#prebuilt-images), but you should feel free to create your own, since that's the purpose of this tool.

And you should tell the tool which target directory you'd like to use for rpm output; this directory will be bound straight to %{_rpmdir} inside the build container, so mind that if your build process does something strange with it, files can be deleted. If the target directory doesn't exist it will be created.

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

URL-based source/patch downloading, shell spawning on build failure, signing, and always updating the remote images are all supported scenarios.

See [example/from_dir](example/from_dir) for a full example of building with a spectemplate from a directory.

## Spectemplates

The spectemplate approach prevents you from editing the .spec file (or creating a new one) for each build; inside your .spectemplate, just define
substitution tags, which are names between @s, e.g.

```
@BUILD_NUMBER@
```

If there's an environment variable called BUILD_NUMBER when you build your project, such variable will be substituted straight into your spec. This is especially useful in an CI server which builds your packages. See the [examples](#examples) section as well.

Please note: you can't have both a .spec and a .spectemplate in your source directory. That will cause an error.

Spectemplates are automatically compiled when using the **dir** command, but can be manually generated with the **genspec** command (see below).

## Manually generating specfile to enable caching of build dependencies

Take a look at [example/from_remote_source](example/from_remote_source) - the whole idea is:

* create a [Dockerfile](example/from_remote_source/build-image/Dockerfile) with your build image. It should inherit from your build platform, add the .spec you're generating in the step below, and call **yum-builddep** on it.
* In the main directory, create a [Makefile](example/from_remote_source/Makefile) (or a shell script) which creates the .spec from the spectemplate into the build-image directory and then builds the docker image. **In this phase, you should complete your spectemplate variables with static values which are not taken from your  build environment**, because they're used for caching: the *genspec* command won't overwrite the generated .spec if it's identical to the existing one, and docker won't build again an image if the input files and the Dockerfile are identical; hence, the build-image will be rebuilt **only if you change your spectemplate or you modify your Dockerfile**.
* Once you've built the build-image, use it with the *dir* command (or even the *srcrpm* command if you prefer, but in such case you can skip the templating-related part altogether) - this time let the build system set the environment variables!
* If your BuildRequires depends on template variables, you shouldn't use this method.

## Rebuilding a source RPM

Rebuilding a .src.rpm file is supported as well. Just check the command:

```
docker-rpm-builder srcrpm --help
```

Verification of the .src.rpm signature, signing, spawning a shell on failure and always updating the build image are all supported scenarios.

## Build images

Build images are nothing esoteric. They're just plain OS images with a set of packages, settings and maybe some macros which are needed to perform a build and/or to sign packages. See the [next section](#prebuilt-images) for some examples.

In order to use an image for building an RPM:

- rpmbuild must exist in path
- yum-builddep must exist in path and accept a .spec file or a .src.rpm as input
- commands must be able to complete without interaction - consider using a custom yum.conf with *main->assumeyes=1* and be sure all public keys for your repositories are installed.
- if you want to sign packages, make sure you install **gnupg** 1.4 and set a proper **%__gpg_sign_cmd** macro in */etc/rpm*
- any other build dependencies should be there, but if your package doesn't build because it's missing something else then the proper
thing to do is probably add an entry to *BuildRequires* in the spec file.

### Prebuilt images

There are some prebuilt configurations for Centos+EPEL and Fedora at [https://github.com/alanfranz/docker-rpm-builder-configurations](https://github.com/alanfranz/docker-rpm-builder-configurations); those are available on [my docker hub page](https://hub.docker.com/u/alanfranz/) as well, so they can be used immediately out of the box.

## Gotchas
* if you're used to mock, the build system is a bit different, mocks seems to employ different defaults and has different macros, sometimes a build working with mock may fail with docker-rpm-builder. I'm investigating the issue. It's quite uncommon BTW.
* dns default to public ones, will add an option for private ones. Right now you can just pass arbitrary docker options, so pass --dns and/or set your internal
DNS in the docker config file.

## Thanks

To all the people who gave me feedback or contributed to this project, in no special order:

* Brian Lalor
* Tobias Widén
* Romain P
* Pavel Borzenkov

## TODOS and ideas
* Remove wget dependency
* Option to prevent container removal after build.

## Disclaimer

This project is not affiliated with Fedora nor RedHat.
