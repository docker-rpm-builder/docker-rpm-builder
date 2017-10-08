#!/bin/bash
set -ex
echo "starting $0"
SPECS_DIR=$(rpm --eval %{_specdir})
SPEC=$(ls ${SPECS_DIR}/*.spec | head -n 1)
touch /var/lib/rpm/*
BUILDDEP_COMMAND="yum-builddep"
command -v dnf && { BUILDDEP_COMMAND="dnf builddep" ; dnf clean metadata ; }
${BUILDDEP_COMMAND} -y --nogpgcheck ${SPEC}
