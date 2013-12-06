#!/bin/bash
set -e
SRCRPM=$(ls /src/*.spec | head -n 1)
yum-builddep ${SRCRPM}
cp -t /docker-rpm-build-root/SOURCES -r /src/*
cp -t /docker-rpm-build-root/yum.repos.d /src/*.repo || /bin/true
rpmbuild -bb $SRCRPM
cp -r /docker-rpm-build-root/RPMS /src
