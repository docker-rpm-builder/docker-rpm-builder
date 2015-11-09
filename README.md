# Fast native RPM building from any distro, for any distro, via docker.

## News

See the [News Page](https://github.com/alanfranz/docker-rpm-builder/wiki/News) for the latest news.

## Preamble

While other deployment systems are at rage today, software delivery via RPM is still pretty widespread; its integration with the distributions' own tools makes it a good choice in many environments.

But RPM building can be painful, especially when native code is involved; building through [rpmbuild](http://www.rpm.org/max-rpm-snapshot/ch-rpm-b-command.html) requires the proper dependencies to be setup on the very same distribution that should be targeted, and making sure that the build system is "clean" - i.e. that no hidden dependency exists, is complex.

More often than not RPM building from scratch is an iterative and frustrating process, requiring a lot of time to succeed.

Tools have been created to ensure build isolation and repeatability; [mock](https://fedoraproject.org/wiki/Projects/Mock) seems to be the most used, but it comes with its own set of problems - it's slow, since it relies on chroots that get created and untarred every time; it's hard to debug when problems happen and why, since there's a lot of code being employed at all time, and seeing what's happening "inside the build" requires manually re-executing a lot commands.

And, last but not least, mock doesn't reliably work on non-RPM based distribution, making it difficult to create the initial RPM on the developer's machine if an RPM-based distro is not employed.

RPM by itself is not very suited to a continuous integration environment, requiring a .src.rpm to be created before the binary RPM can be generated; this is often unnecessary in today's environments where the source tracking occurs on VCS systems, and again, slows the whole process down.

## Key features

**docker-rpm-builder** works on any host distributions that supports [docker](https://www.docker.com/), and is currently tested to build 64 bit Centos 5, 6 and 7 RPM packages, as well as Fedora 20, 21, 22, and rawhide.

It's designed to be a very **small and hackable wrapper** to help in rpm building, and lets you build binary RPMs on the fly, **without generating an intermediate source rpm** - which is required by tools like *mock* and it's a bit of an unnecessary byproduct nowadays, since most source tracking is done in a revision control system. Docker capabilities are leveraged to make the build **fast**; copy is limited, and bind-mount between host and container is privileged whenever it's possible.

It leverages the standard RPM creation system - it's **not** a different build system like [fpm](https://github.com/jordansissel/fpm), which has its own options and wraps different distributions' build tools.

It **improves** the standard RPM creation system by letting builds happen straight from a source directory - and by **adding a templating layer** over the .spec files which lets variables to be easily injected - this is especially useful in a continuous integration environment, where a build number and/or a reference VCS commit can be integrated.

It's highly **debuggable** - with the proper option set, whenever a build failure occurs, an interactive shell is spawned in the very context of the build.

It's **fast** (benchmarks are going to happen soon, I'm trying to perform some reproducible tests right now and I plan to add them to the repo) - by leveraging Docker capabilities there's very little copy happening between builds; such minimal IO speeds things up. But the real performance improvement
comes from the ease of use from any host system, from the interactive shell spawning and from the great hackability to suit your build needs.

The root filesystem is *fully writable* - this is very handy if you've got an application that in some way hardcodes paths when installed,
and you get errors because paths like "/tmp/buildroot-something" found in files. Just install it in the place it's meant to be installed and
move it to ```${RPM_BUILD_ROOT}``` afterwards.

Builds done in such fashion are **highly reproducible** - if your build image already contains all the build dependencies, and you disable docker network,
the same build input will always yield the same output. This does not mean that files would be 100% identical, there may be build-time changes
depending e.g. on current time - but no external influence is possible (assuming that you're always using the same host kernel).

## Limitations

* Currently limited to x86_64 for both host and target. That's a docker limitation which is unlikely to go away soon. 32 bit images for Docker do exist, but they're considered unsupported by this tool.

## Required knowledge

You should have a vague idea of what [docker](https://www.docker.com) is and you should already know how to build an RPM - see to [Maximum RPM](http://www.rpm.org/max-rpm/) and other documentation from Fedora [HowTO](https://fedoraproject.org/wiki/How_to_create_an_RPM_package) [RPM Guide](http://docs.fedoraproject.org/en-US/Fedora_Draft_Documentation/0.1/html/RPM_Guide/).

## Prerequisites

At the dawn of this tool, I tried to make it work with any version of *docker* that would come from the distributions' repository or from official repository. This proved to be quite troublesome, and the docker environment is advancing rapidly; it makes no sense to use or support older versions of *docker*.

So, **docker >= 1.8** is currently a prerequisite. If you're using the prebuilt RPMs or DEBs, they expect the **docker-engine** package from yum.dockerproject.org or apt.dockerproject.org to be available; just follow the [official install instructions](https://docs.docker.com/engine/installation/).

See the [docker configuration](#docker-configuration) section for details on some post-install actions for docker.

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

And you're done; skip to the [docker configuration](#docker-configuration) section.

### Fedora 20/21/22

If you're using a pre-release Fedora version (F23 at this time) or rawhide, you may experience better luck with the
install from source method.

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

And you're done; skip to the [docker configuration](#docker-configuration) section.

### Debian and Ubuntu

There're repositories for those distributions; you'll need to enable the official docker package from docker.io [see install docs](https://docs.docker.com/installation/) or docker-rpm-builder will fail to install.

**Only Ubuntu Trusty is actively tested!**. Please report issues with other distributions' packages.

First, you should make sure that you've got my package signing key properly installed and configured for apt:
```
curl https://www.franzoni.eu/keys/D1270819.txt | sudo apt-key add -
```

Then, pick the proper repo for your distribution - see next sections - and save it as **/etc/apt/sources.list.d/docker-rpm-builder.list**

Now you're ready to

```
apt-get update
apt-get -y install docker-rpm-builder
```

Enjoy!

#### Ubuntu Trusty

```
deb http://www.a9f.eu/apt/docker-rpm-builder-v1/ubuntu trusty main
```
#### Ubuntu Utopic

```
deb http://www.a9f.eu/apt/docker-rpm-builder-v1/ubuntu utopic main
```

#### Ubuntu Vivid

```
deb http://www.a9f.eu/apt/docker-rpm-builder-v1/ubuntu vivid main
```


#### Debian Wheezy

```
deb http://www.a9f.eu/apt/docker-rpm-builder-v1/debian wheezy main
```

#### Debian Jessie

```
deb http://www.a9f.eu/apt/docker-rpm-builder-v1/debian jessie main
```



### Other distributions

You can just use the [docker-rpm-builder python package](https://pypi.python.org/pypi/docker-rpm-builder/) and manually configure the system by yourself; the following steps will guide you in such process.

#### Prerequisites

You must have [docker](https://www.docker.com/) >= 1.8 installed and properly configured (see the [install docs](https://docs.docker.com/installation/#installation) and the [docker configuration](#docker-configuration) section.

Python 2.7, bash, and wget should be installed on your system as well.

#### Installation from pypi

docker-rpm-builder is a pure Python package; if you know python packaging works,
I recommend you just create a virtualenv and ```pip install docker-rpm-builder``` inside it.
You'll get a ```docker-rpm-builder``` executable in the env's bin directory.

If you don't know how python packaging works, here's a quick guide to installing
docker-rpm-builder.

First, verify *python2.7* is available on your system

```
~/bin$ python --version
Python 2.7.6
```

*There may be multiple Python versions installed on your system; check for pythonX.X
executables, and use such executables everywhere in the following steps. If multiple Python versions are installed
you could probably find multiple virtualenv executables like virtualenv-X.X as well*

Then, check whether an executable called ```pip``` is available in your system;
it's probably installed by default on most Linux distributions that offer Python as well.
If it isn't installed, and it's not available in your package manager, you need to
[install it](https://pip.pypa.io/en/latest/installing.html), which probably means
something like:

**PLEASE NOTE:** If you've got a distribution shipping an outdated version of pip,
you may want to update it, maybe on a per-user basis.

##### Installing an up-to-date pip system-wide

```
curl https://bootstrap.pypa.io/get-pip.py | sudo python
```

##### Installing a local up-to-date pip for the current user.

```
curl https://bootstrap.pypa.io/get-pip.py > get-pip.py && python get-pip.py --user
```

This will add the pip executable to .local/bin; make sure it's in your PATH.

##### Going on

Once you've got pip in place, I recommend using [pipsi](https://github.com/mitsuhiko/pipsi)
to install docker-rpm-builder; it's a tool that will create an isolated environment for
a package along with dependencies, without polluting the global environment. Make
sure ~/.local/bin is in your PATH, then execute something like (remove the --user flag if you want to install it globally):

```
pip install --user virtualenv pipsi
```

and then

`````
pipsi install docker-rpm-builder
```

And you'll find a ready-to-use *docker-rpm-builder* executable in ~/.local/bin .

To get a more recent version, just use:

```
pipsi upgrade docker-rpm-builder
```

pipsi work for any python package that should run in an isolated environment; it's a good
idea to use it a lot.

## Docker configuration

If docker is already up and running on your system, you probably need to do absolutely nothing else.

Otherwise, if it's your first time with docker, here's a checklist:

* Verify the *docker* service is running
* Verify the *docker* group exists and your user belongs to it. It is advised **not to run docker-rpm-builder as root**. The docker package on some recent Fedoras seems to add a *dockerroot* group instead - **it won't do!**
* If you had to add the group, verify you've restarted the *docker* service after such addition
* Verify you've logged out+in after adding your user to the group
* Verify selinux is disabled. There seems to be work going on to let docker work along selinux, but I could not succeed at using bindmounts as long as selinux is active.
* Verify your disk has enough free space

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

It will take a really long time to run, especially the first time.

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
i


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




## Spectemplates

The spectemplate approach prevents you from editing the .spec file (or creating a new one) for each build; inside your .spectemplate, just define
substitution tags, which are names between @s, e.g.

```
@BUILD_NUMBER@
```

If there's an environment variable called BUILD_NUMBER when you build your project, such variable will be substituted straight into your spec. This is especially useful in an CI server which builds your packages. Consider the .spectemplate for this very project, [docker-rpm-builder.spectemplate](docker-rpm-builder.spectemplate) , and you can see the @BUILD_NUMBER@ and @GIT_COMMIT@ substitution variables at work; those are set by the [Jenkins](http://jenkins-ci.org/) build system.

Please note: you can't have both a .spec and a .spectemplate in your source directory. That will cause an error.

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

There are some prebuilt configurations for Centos 5-6-7+EPEL and Fedora 20-21-rawhide at [https://github.com/alanfranz/docker-rpm-builder-configurations](https://github.com/alanfranz/docker-rpm-builder-configurations); those are available on [my docker hub page](https://hub.docker.com/u/alanfranz/) as well, so they can be used immediately out of the box. The following are all valid build images:

- alanfranz/drb-epel-5-x86-64:latest
- alanfranz/drb-epel-6-x86-64:latest
- alanfranz/drb-epel-7-x86-64:latest
- alanfranz/drb-fedora-20-x86-64:latest
- alanfranz/drb-fedora-21-x86-64:latest
- alanfranz/drb-fedora-rawhide-x86-64:latest

## Speedup your build: image reuse

The impact of this change can be great if you're building a small package with a lot of frequency.

In such situation, the dependency download time can just waste any speed that you could gain by using this tool.

So what?

Well, just use an image which pre-caches your build dependencies!

create a directory like *build-image* in your project directory;
let's suppose your project needs openssl and openssl-devel to build
on Centos 6.

Enter something like this in your newly created *Dockerfile*:

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
* General refactor: remove code duplication, improve setup, etc. - things are currently quite messed up.
* Support some way to cache build dependencies between builds for the same package (commit after run? commit after build-dep?)
* Refactor bash-based test into python-based ones, even when spawning processes
* Option for creating a Dockerfile with build dependencies for a package, that can be used for
  repeatable builds and/or caching.

## Disclaimer

This project is not affiliated with Fedora nor RedHat.
