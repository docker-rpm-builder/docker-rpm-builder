#!/bin/bash
set -ex
echo "starting $0"
SPEC=$(ls /docker-rpm-build-root/SOURCES/*.spec | head -n 1)
/dockerscripts/rpm-setup-deps.sh
#rpmbuild complains if it can't find a proper user for uid/gid
groupadd -g $2 mygroup || /bin/true
useradd -g $2 -u $1 myuser || /bin/true
rpmbuild -bb $SPEC || /bin/bash
chown -R $1:$2 /docker-rpm-build-root/RPMS/*
echo "Done"
