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
[ -z "${GPG_PRIVATE_KEY}" ] && { echo "Private key not passed; rpm won't be signed"; }


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
yum-builddep -y --nogpgcheck "${SRPMS_DIR}/${SRCRPM}"

if [ -n "${GPG_PRIVATE_KEY}" ]
then
    echo "Running with RPM signing"
    echo -e "${GPG_PRIVATE_KEY}" | gpg --import
    [[ $(gpg --list-secret-keys) =~ uid(.*) ]]
    KEYNAME="${BASH_REMATCH[1]}"
    [ -n "${KEYNAME}" ] || { echo "could not find key for signing purpose"; exit 1; }
    echo -e "%_gpg_name ${KEYNAME}\n%_signature gpg" > ${HOME}/.rpmmacros
    echo -e "\n" | setsid rpmbuild --sign --rebuild ${RPMBUILD_OPTIONS} "${SRPMS_DIR}/${SRCRPM}" ||  { [ "bashonfail" == "${BASH_ON_FAIL}" ] && { echo "Build failed, spawning a shell" ; /bin/bash ; exit 1; } || /bin/false ; }
else
    rpmbuild --rebuild ${RPMBUILD_OPTIONS} "${SRPMS_DIR}/${SRCRPM}" || { [ "bashonfail" == "$BASH_ON_FAIL" ] && { echo "Build failed, spawning a shell" ; /bin/bash ; exit 1; } || /bin/false ; }
fi

echo "Done"


