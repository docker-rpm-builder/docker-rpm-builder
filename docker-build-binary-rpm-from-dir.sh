#!/bin/bash
set -ex
IMAGETAG=$1
[ -n $1 ] || { echo "Missing IMAGETAG param" ; exit 1 ;}
shift 1
SRCDIR=$1
[ -n $1 ] || { echo "Missing SRCDIR" ; exit 1 ;}
shift 1
SRCDIR=$(readlink -f ${SRCDIR})
echo "Now building project from $SRCDIR on image $IMAGETAG"

CURRENTDIR=$(dirname $(readlink -f $0))

docker run $* -v ${CURRENTDIR}/docker-scripts:/docker-scripts -v ${SRCDIR}:/src -w /docker-scripts ${IMAGETAG} ./rpmbuild-in-docker.sh
