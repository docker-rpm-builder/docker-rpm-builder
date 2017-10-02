#!/bin/bash
set -ex
echo "starting $0"
SPECS_DIR=$(rpm --eval %{_specdir})
SPEC=$(ls ${SPECS_DIR}/*.spec | head -n 1)
touch /var/lib/rpm/*
dnf clean metadata
dnf builddep -y --nogpgcheck ${SPEC}
