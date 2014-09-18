#!/bin/bash
set -ex
echo "starting $0"
SPEC=$(ls /src/*.spec | head -n 1)
cp -t /docker-rpm-build-root/SOURCES -r /src/*
[ -x /src/drb-pre ] && /src/drb-pre
/docker-scripts/rpm-setup-deps.sh
rpmbuild -bb $SPEC
[ -x /src/drb-post ] && /src/drb-post
cp -fr /docker-rpm-build-root/RPMS /src
echo "Done"
