#!/bin/bash
set -ex
echo "starting $0"
SPEC=$(ls /src/*.spec | head -n 1)
mkdir -p /docker-rpm-build-root/SOURCES/hostdir
cp -t /docker-rpm-build-root/SOURCES/hostdir -r /src/*
[ -x /src/drb-pre ] && /src/drb-pre
/dockerscripts/rpm-setup-deps.sh
rpmbuild -bb $SPEC || /bin/bash
[ -x /src/drb-post ] && /src/drb-post
chown -R $1 /docker-rpm-build-root/RPMS
echo "Done"
