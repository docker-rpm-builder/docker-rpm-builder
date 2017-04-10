## next release:
- Remove overlayfs support, it's too unreliable  (depends on kernel version, underlying fs type, etc)

## 04 Mar 2017: docker-rpm-builder v1.37
- Fix hardcoded --download-sources option in chainbuild. The option must be enabled manually.

## 07 Jan 2017: docker-rpm-builder v1.36
- SELinux context support; makes it possible to use docker-rpm-builder even when SELinux is enabled.

## 06 Jan 2017: docker-rpm-builder v1.35 
- New **chainbuild** command that allows the user to build a .src.rpm, then build a binary rpm from that.

## 04 Jan 2017: docker-rpm-builder v1.34
- Don't enforce a dep on a specific docker distribution
- Drop support for ubuntu wily
- Add support for fc25 and ubuntu yakkety

## 03 Jan 2017: docker-rpm-builder v1.33 (failed release - skip)

## 01 Dec 2016: public repositories are moving!
I'm going to move my public RPM and DEB repositories to bintray; if you encounter a 404, 410 or other error when trying to update docker-rpm-builder in the upcoming weeks, get back to my homepage and check the new url.

## 01 Aug 2016: docker-rpm-builder v1.32
- Fedora 24 and docker 1.12 support.

## 13 May 2016: docker-rpm-builder v1.31
- Definitive solution for the additional docker options issue.

## 6 May 2016: docker-rpm-builder v1.28
- Fix an issue with additional docker options being escaped while they shouldn't.

## 3 May 2016: docker-rpm-builder v1.27
- Supports overlay for %{_sourcedir} if enabled in kernel - allows modifications of source directory that aren't propagated to the host filesystem.
- Can pass a ```--env=RPMBUILD_EXTRA_OPTIONS=...``` via additional docker options, such env will be interpreted and passed to rpmbuild inside the container for further customization.
- Ubuntu Xenial packages.

## 28 Feb 2016: docker-rpm-builder v1.26
- Some documentation cleanup, clarify requirements and support for different host distros
- Try working properly (source install) even in deeply nested directories
- Unofficially support 32 bit images in our test suite
- Workaround docker 1.10 ```run --rm``` header issues
- Use ```rpmsign``` instead of ```rpmbuild --sign``` to sign packages; this seems to be more forward-compatibile, 
  as the latter option is deprecated and already had issues on modern Fedoras guests
- Support preserving containers used for the build, with a dedicated flag; useful for debugging purposes.

## 13 Feb 2016: docker-rpm-builder v1.25
- Fixed a build issue that would lead to unsigned rpm packages
- Fixed an issue with debug mode
- added the genspec command to resolve a spectemplate; useful for build-time caching.

## 3 Feb 2016: docker-rpm-builder v1.24
- only available via packages or via git source. No releases will be done on pypi anymore.
- supports OSX. Currently tested on El Capitan via docker-machine only.
- general refactor and cleanup: code should be far easier to understand now.
- removed all bash-based testing code.
- automated testing of the package for all target host distributions via Vagrant, for more reliable packaging
- packaging is now done in a more consistent fashion, via fpm-within-docker.
- updated docs.

## 13 Nov 2015: change in the release procedure
- My build/release system for docker-rpm-builder is driving me a bit crazy, and will change soon.
 I won't release the tool anymore on pypi.python.org, if you like to install from source you'll
 need cloning this repo and install pseudo-manually.

## 22 Sep 2015: docker-rpm-builder v1.23
- This release supports and requires docker 1.8, which is available at a different repository. Please check again the install pages for your distribution and make sure to update. The new official package from *docker* is named *docker-engine*.
- Fedora: I won't support beta releases nor rawhide anymore. The rapid development of such distributions makes it very easy to fail builds when there's nothing inherently wrong in my software. If you're running such bleeding edge distros, please consider following the instructions to install from source.

## 21 May 2015: docker-rpm-builder v1.22
**this update is available on a9f.eu only! update your repositories!**
- fix: look for rpmbuild path inside the container
- fix: make sure we use a consistent charset when writing the temporary specfile after spectemplate interpolation

## 15 May 2015: docker-rpm-builder v1.21
- small fix: output a proper warning if somebody is using older repositories.

This version will be the last that shall be published to packagecloud; refer to the new repositories
from now on. They already contain the most recent versions of docker-rpm-builder.

## 14 May 2015: docker-rpm-builder v1.20

Changes:
- better support for sources downloading that doesn't rely on the host's spectool
- .spec file, when using a spectemplate, is not written to the source directory anymore
- source directory and specfiles are mounted readonly inside the container to prevent potential changes from inside the build environment.

## 14 May 2015: new repositories

I think I've found a solutions for repository hosting that can satisfy me. The new URLs are live now.
Please forgive me for the multiple switches.

## 27 Apr 2015: Repositories will change again

I'm currently unsatisfied with something about the current way to host packages, both for Apt and Yum; repositories will change again soon. Stay tuned.

## 10 Apr 2015: Debian and Ubuntu repositories

Beyond Centos & Fedora, now you can download docker-rpm-builder straight from an apt repository. Check the main [README](https://github.com/alanfranz/docker-rpm-builder/blob/v1/README.md).

## New Repositories!

New repositories are available on packagecloud. The others will be discontinued. Just check the main [README](https://github.com/alanfranz/docker-rpm-builder/blob/v1/README.md)

# Releases

## 1.14
 * Fix: a small glitch with base64 decoding inside the container
 * Fix: don't spawn an interactive shell if something bad happens when fetching dependencies

## 1.8

* Fix some small glitches with ownership inside the container
* let the user choose the output ownership
* Add test to verify our scripts are executable
* Cleanup install instructions
* Remove dependency on assumeyes for yum.conf

## 1.7 

First public working release.
