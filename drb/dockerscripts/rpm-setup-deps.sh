#!/bin/bash
set -ex
echo "starting $0"
SPEC=$(ls /docker-rpm-build-root/SOURCES/*.spec | head -n 1)
# allow the user to overwrite our yum.conf if he likes, otherwise use .repo files.
{ cp /docker-rpm-build-root/SOURCES/yum.conf /etc && echo "yum.conf was overriden! custom repos files will be ignored." ; }
{ cp -t /docker-rpm-build-root/yum.repos.d /docker-rpm-build-root/SOURCES/*.repo && echo "custom repo files were added" ; }
yum-builddep --nogpgcheck ${SPEC} || /bin/bash
