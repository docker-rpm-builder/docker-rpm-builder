#!/bin/bash
set -ex
# verify: security implications.
[ -z "$1" ] && { echo "Missing parameters"; /bin/false; }
eval $(echo $1 | base64 -d)

[ -z "${SRCRPM}" ] && { echo "Missing SRCRPM"; /bin/false; }
[ -z "${CALLING_UID}" ] && { echo "Missing CALLING_UID"; /bin/false; }
[ -z "${CALLING_GID}" ] && { echo "Missing CALLING_GID"; /bin/false; }
[ -z "${RPMBUILD_OPTIONS}" ] && { echo "No rpmbuild options were set"; }
[ -z "${BASH_ON_FAIL}" ] && { echo "BASH_ON_FAIL is not set"; }


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

rpmbuild --rebuild ${RPMBUILD_OPTIONS} "${SRPMS_DIR}/${SRCRPM}" || { [ "bashonfail" == "$BASH_ON_FAIL" ] && { echo "Build failed, spawning a shell" ; /bin/bash ; exit 1; } || /bin/false ; }


