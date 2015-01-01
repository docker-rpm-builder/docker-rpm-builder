#!/bin/bash
set -ex
SRCRPM=$1
CALLING_UID=$2
CALLING_GID=$3
RPMBUILD_OPTIONS=$4

RPMS_DIR=$(rpm --eval %{_rpmdir})
SRPMS_DIR=$(rpm --eval %{_srcrpmdir})

function finish {
  chown -R ${CALLING_UID}:${CALLING_GID} ${RPMS_DIR} || /bin/true
}
trap finish EXIT
echo "starting $0"

#rpmbuild complains if it can't find a proper user for uid/gid
groupadd -g ${CALLING_GID} mygroup || /bin/true
useradd -g ${CALLING_GID} -u ${CALLING_UID} myuser || /bin/true

yum-builddep --nogpgcheck "${SRPMS_DIR}/${SRCRPM}"

rpmbuild --rebuild ${RPMBUILD_OPTIONS} "${SRPMS_DIR}/${SRCRPM}"


