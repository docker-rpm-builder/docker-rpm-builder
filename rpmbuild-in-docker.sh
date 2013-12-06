#!/bin/bash
set -e
SRCRPM=$(ls /src/*.spec | head -n 1)
yum-builddep ${SRCRPM}
cp -t /docker-rpm-build-root/SOURCES -r /src/*
# allow the user to overwrite our yum.conf if he likes, otherwise use .repo files.
{ cp /src/yum.conf /etc && echo "yum.conf was overriden, .repo files will be ignored" ; } ||  { { cp -t /docker-rpm-build-root/yum.repos.d /src/*.repo && echo "no repo was added" ; } || /bin/true ; }
rpmbuild -bb $SRCRPM
cp -r /docker-rpm-build-root/RPMS /src
