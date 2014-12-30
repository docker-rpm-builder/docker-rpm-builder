#!/bin/bash
set -ex
SRCRPM=$1
CALLING_UID=$2
CALLING_GID=$3

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

# extract the source rpm just to fetch the
# pushd $(mktemp -d)
# rpm2cpio "${SRPMS_DIR}/${SRCRPM}" | cpio -iv --make-directories
yum-builddep "${SRPMS_DIR}/${SRCRPM}"
# popd

rpmbuild --rebuild "${SRPMS_DIR}/${SRCRPM}"


