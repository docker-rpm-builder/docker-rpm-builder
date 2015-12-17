#!/bin/bash
set -ex

[ -z "${CALLING_UID}" ] && { echo "Missing CALLING_UID"; /bin/false; }
[ -z "${CALLING_GID}" ] && { echo "Missing CALLING_GID"; /bin/false; }
[ -z "${BASH_ON_FAIL}" ] && { echo "Missing BASH_ON_FAIL. Won't drop into interactive shell if errors are found"; }

RPMS_DIR=$(rpm --eval %{_rpmdir})
SRPMS_DIR=$(rpm --eval %{_srcrpmdir})
SOURCE_DIR=$(rpm --eval %{_sourcedir})
SPECS_DIR=$(rpm --eval %{_specdir})

function finish {
  chown -R ${CALLING_UID}:${CALLING_GID} ${RPMS_DIR} || /bin/true
}
trap finish EXIT

echo "starting $0"
SPEC=$(ls ${SPECS_DIR}/*.spec | head -n 1)
/dockerscripts/rpm-setup-deps.sh

#rpmbuild complains if it can't find a proper user for uid/gid of the source files;
#we should add all uid/gids for source files.
for gid in $(stat -c '%g' ${SOURCE_DIR}/*); do
    groupadd -g $gid "group$gid" || /bin/true
done

for uid in $(stat -c '%u' ${SOURCE_DIR}/*); do
    useradd -u $uid "user$uid" || /bin/true
done


if [ -r "/private.key" ]
then
    echo "Running with RPM signing"
    gpg --import /private.key
    [[ $(gpg --list-secret-keys) =~ uid(.*) ]]
    KEYNAME="${BASH_REMATCH[1]}"
    [ -n "${KEYNAME}" ] || { echo "could not find key for signing purpose"; exit 1; }
    echo -e "%_gpg_name ${KEYNAME}\n%_signature gpg" > ${HOME}/.rpmmacros
    echo -e "\n" | setsid rpmbuild -bb --sign $SPEC ||  { [ "bashonfail" == "${BASH_ON_FAIL}" ] && { echo "Build failed, spawning a shell" ; /bin/bash ; exit 1; } || /bin/false ; }
else
    echo "Running without RPM signing"
    rpmbuild -bb $SPEC || { [ "bashonfail" == "${BASH_ON_FAIL}" ] && { echo "Build failed, spawning a shell" ; /bin/bash ; exit 1; } || /bin/false ; }
fi
echo "Done"
