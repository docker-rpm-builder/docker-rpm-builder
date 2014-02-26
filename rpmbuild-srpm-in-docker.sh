#!/bin/bash
set -e
SRCRPM=$(ls /src/*.src.rpm | head -n 1)
# allow the user to overwrite our yum.conf if he likes, otherwise use .repo files.
{ cp /src/yum.conf /etc && echo "yum.conf was overriden, .repo files will be ignored" ; } ||  { { cp -t /docker-rpm-build-root/yum.repos.d /src/*.repo && echo "no repo was added" ; } || /bin/true ; }
yum-builddep -y ${SRCRPM}
rpmbuild --rebuild $SRCRPM
cp -r /docker-rpm-build-root/RPMS /src
