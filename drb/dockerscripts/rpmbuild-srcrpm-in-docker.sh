#!/bin/bash
set -ex
SRCRPM=$1
CALLING_UID=$2
CALLING_GID=$3
RPMBUILD_OPTIONS=$4
BASH_ON_FAILURE=$5

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

# we don't check the gpg signature at this time, we don't really care;
# if the signature check fails it will fail later.
yum-builddep --nogpgcheck "${SRPMS_DIR}/${SRCRPM}"

rpmbuild --rebuild ${RPMBUILD_OPTIONS} "${SRPMS_DIR}/${SRCRPM}" || { [ "bashonfail" == "$BASH_ON_FAILURE" ] && { echo "Build failed, spawning a shell" ; /bin/bash ; exit 1; } || /bin/false ; }


