#!/bin/bash
set -ex
echo "starting $0"
SPEC=$(ls /src/*.spec | head -n 1)
mkdir -p /docker-rpm-build-root/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
cp -t /docker-rpm-build-root/SOURCES -r /src/*
chown -R root. /src
yum-builddep "$SPEC" -y
spectool --directory /docker-rpm-build-root/SOURCES -g "$SPEC"
rpmbuild -ba --define="_topdir /docker-rpm-build-root" "$SPEC"
cp -r /docker-rpm-build-root/SRPMS /src
cp -r /docker-rpm-build-root/RPMS /src
echo "Done"
