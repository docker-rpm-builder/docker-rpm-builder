#!/bin/bash
set -ex
echo "starting $0"
SOURCE_DIR=$(rpm --eval %{_sourcedir})
SPEC=$(ls ${SOURCE_DIR}/*.spec | head -n 1)
yum-builddep --nogpgcheck ${SPEC} || /bin/bash
