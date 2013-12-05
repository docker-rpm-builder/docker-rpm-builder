#!/bin/bash
set -ex
IMAGETAG=$1
[ -n $1 ] || { echo "Missing IMAGETAG param" ; exit 1 ;}
SRCRPM=$2
[ -n $2 ] || { echo "Missing .src.rpm param" ; exit 1 ;}
docker run -v `pwd`:/docker-srpmbuild -w /docker-srpmbuild $IMAGETAG ./rpmbuild-in-docker.sh $SRCRPM
