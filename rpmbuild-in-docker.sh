#!/bin/bash
set -ex
echo "starting $0"
SPEC=$(ls /src/*.spec | head -n 1)
cp -t /docker-rpm-build-root/SOURCES -r /src/*
# allow the user to overwrite our yum.conf if he likes, otherwise use .repo files.
{ cp /src/yum.conf /etc && echo "yum.conf was overriden" ; } 
{ cp -t /docker-rpm-build-root/yum.repos.d /src/*.repo && echo "custom repo files were added" ; } 
yum-builddep ${SPEC}
rpmbuild -bb $SPEC
cp -r /docker-rpm-build-root/RPMS /src
echo "Done"
