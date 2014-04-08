#!/bin/bash
set -ex
echo "starting $0"
SPEC=$(ls /src/*.spec | head -n 1)
cp -t /docker-rpm-build-root/SOURCES -r /src/*
rpmbuild -bb $SPEC
cp -r /docker-rpm-build-root/RPMS /src
echo "Done"
