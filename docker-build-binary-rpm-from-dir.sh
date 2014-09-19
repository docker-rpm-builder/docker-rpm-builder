#!/bin/bash
set -e
USAGE="Usage:\n$0 IMAGETAG SRCDIR <...additional docker options..>\n"
IMAGETAG=$1
[ -n "$1" ] || { echo "ERROR: Missing IMAGETAG param" ; echo -e $USAGE ; exit 1 ;}
shift 1
SRCDIR=$1
[[ -n "$1" && -d $1 && -r $1 && -x $1 && -w $1 ]] || { echo "ERROR: Missing SRCDIR or wrong permissions - must be an rwx directory" ; echo -e $USAGE ; exit 1 ;}
shift 1
SRCDIR=$(readlink -f ${SRCDIR})
echo "Now building project from $SRCDIR on image $IMAGETAG"

CURRENTDIR=$(dirname $(readlink -f $0))

docker run $* -v ${CURRENTDIR}/docker-scripts:/docker-scripts -v ${SRCDIR}:/src -w /docker-scripts ${IMAGETAG} ./rpmbuild-in-docker.sh $(id -u):$(id -g)
