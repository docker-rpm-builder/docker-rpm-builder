#!/bin/bash
set -ex
IMAGETAG=$1
[ -n $1 ] || { echo "Missing IMAGETAG param" ; exit 1 ;}
SRCDIR=$2
[ -n $2 ] || { echo "Missing SRCDIR" ; exit 1 ;}
docker run --dns=10.2.0.1 -v `pwd`:/docker-files -v ${SRCDIR}:/src -w /docker-files $IMAGETAG ./rpmbuild-in-docker.sh
