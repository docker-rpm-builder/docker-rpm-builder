#!/bin/bash
# $1 is calling user uid, $2 is calling user gid, $3 is whether to spawn bash on fail.
set -ex
echo "starting $0"
SPEC=$(ls /docker-rpm-build-root/SOURCES/*.spec | head -n 1)
/dockerscripts/rpm-setup-deps.sh
#rpmbuild complains if it can't find a proper user for uid/gid
groupadd -g $2 mygroup || /bin/true
useradd -g $2 -u $1 myuser || /bin/true
rpmbuild -bb $SPEC || {  [ "bashonfail" == "$3" ] && { echo "Build failed, spawning a shell" ; /bin/bash ; } || /bin/false ; }
chown -R $1:$2 /docker-rpm-build-root/RPMS/*
echo "Done"
