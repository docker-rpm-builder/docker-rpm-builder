#!/bin/bash
set -ex
EPEL6_IMAGE="alanfranz/drb-epel-6-x86-64:latest"
RPM_DIR="/tmp/drb_rpms"
rm -rf tmux-src/*.tar.gz
rm -rf ${RPM_DIR}
docker-rpm-builder dir ${EPEL6_IMAGE} tmux-src/ ${RPM_DIR} && { echo "should have failed"; exit 1; } || /bin/true
rm -rf ${RPM_DIR}
docker-rpm-builder dir --download-sources ${EPEL6_IMAGE} tmux-src/ ${RPM_DIR}
[ "$(ls ${RPM_DIR}/x86_64/tmux-* | wc -l)" == "2" ]


