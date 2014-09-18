#!/bin/bash
set -ex
SRCDIR=$1
[ -n $1 ] || { echo "Missing IMAGETAG param" ; exit 1 ;}
shift 1
SPEC=$(basename $(ls $SRCDIR/*.spec | head -n 1))
docker run $*  -v `pwd`:/docker-files -v ${SRCDIR}:/src -w /docker-files ${SPEC}-drb-build  ./rpmbuild-in-docker.sh
