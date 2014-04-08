#!/bin/bash
set -ex
echo "starting $0"
DIR=$1
SPEC=$(basename $(ls $DIR/*.spec | head -n 1))
docker build -t ${SPEC}-drb-build ${DIR}

