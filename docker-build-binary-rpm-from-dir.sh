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

# substitute template if it's there
SPEC=$(ls /${SRCDIR}/*.spec | head -n 1)
SPECTEMPLATE=$(ls /${SRCDIR}/*.spectemplate | head -n 1)
[ -n "${SPEC}" ] && [ -n "${SPECTEMPLATE}" ] && { echo "ERROR: spec and spectemplate can't both be in ${SRCDIR}"; exit 1 ; }
# we must find a better way to create the .spec without polluting source directory
[ -n "${SPECTEMPLATE}" ] && DELETESPEC="y" && perl -p -i -e 's/\$\{([^}]+)\}/defined $ENV{$1} ? $ENV{$1} : $&/eg' < ${SPECTEMPLATE} > ${SPECTEMPLATE%template}

echo "Now building project from $SRCDIR on image $IMAGETAG"

CURRENTDIR=$(dirname $(readlink -f $0))

docker run $* -v ${CURRENTDIR}/docker-scripts:/docker-scripts -v ${SRCDIR}:/src -w /docker-scripts ${IMAGETAG} ./rpmbuild-in-docker.sh $(id -u):$(id -g)
#docker run $* -v ${CURRENTDIR}/docker-scripts:/docker-scripts -v ${SRCDIR}:/src -w /docker-scripts -i -t ${IMAGETAG}  /bin/bash

[ -n "${DELETESPEC}" ] && rm -f ${SPECTEMPLATE%template}

