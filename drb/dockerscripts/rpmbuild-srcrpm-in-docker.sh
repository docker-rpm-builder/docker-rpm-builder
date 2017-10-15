#!/bin/bash
set -ex

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

#rpmbuild complains if it can't find a proper user for uid/gid of the source files;
#we should add all uid/gids for source files.
for gid in $(stat -c '%g' ${SRPMS_DIR}/*); do
    groupadd -g $gid "group$gid" >/dev/null 2>&1 || /bin/true
done

for uid in $(stat -c '%u' ${SRPMS_DIR}/*); do
    useradd -u $uid "user$uid" >/dev/null 2>&1 || /bin/true
done

# we don't check the gpg signature at this time, we don't really care;
# if the signature check fails it will fail later.
yum-builddep -y --nogpgcheck "${SRPMS_DIR}/${SRCRPM}"

if [ -r "/rpmmacros" ]
then
    cp /rpmmacros ${HOME}/.rpmmacros
    echo -e "\n" >> ${HOME}/.rpmmacros
fi

if [ -r "/private.key" ]
then
    echo "Running with RPM signing"
    gpg --import /private.key
    [[ $(gpg --list-secret-keys) =~ uid(.*) ]]
    KEYNAME="${BASH_REMATCH[1]}"
    [ -n "${KEYNAME}" ] || { echo "could not find key for signing purpose"; exit 1; }
    echo -e "%_gpg_name ${KEYNAME}\n%_signature gpg" >> ${HOME}/.rpmmacros
    gpg --armor --export ${KEYNAME} > /tmp/public.gpg
    rpm --import /tmp/public.gpg

	exitcode=0
    rpmbuild_out="$(rpmbuild --rebuild ${RPMBUILD_EXTRA_OPTIONS} ${RPMBUILD_OPTIONS} "${SRPMS_DIR}/${SRCRPM}" 2>&1)" || { exitcode="$?" ; /bin/true ; }
    if [ "${exitcode}" -ne 0 ]; then
			if [ "bashonfail" == "${BASH_ON_FAIL}" ]; then
				# if the build is interactive, we can see what's printed in the current log, no need to reprint.
				echo "Build failed, spawning a shell. The build will terminate after such shell is closed."
				/bin/bash
			else 
				echo -e "${rpmbuild_out}\n\nrpmbuild command failed."
			fi
		exit ${exitcode}
	fi
    
	files="$(sed -n -e '/Checking for unpackaged file/,$p' <<< "${rpmbuild_out}" | grep 'Wrote:' | cut -d ':' -f 2)"
	
	exitcode=0
    echo -e "\n" | setsid rpmsign --addsign ${files} || /bin/true
    rpm -K ${files} || { echo "Signing failed." ; exitcode=1; }
    if [ "${exitcode}" -ne 0 ]; then
			if [ "bashonfail" == "${BASH_ON_FAIL}" ]; then
				# if the build is interactive, we can see what's printed in the current log, no need to reprint.
				echo "Signing failed, spawning a shell. The build will terminate after such shell is closed."
				/bin/bash
			else
				echo -e "${rpmbuild_out}\n\nrpmsign command failed."
			fi
		# don't accidentally retain unsigned files
		rm -f ${files}
		exit ${exitcode}
	fi
else
    rpmbuild --rebuild ${RPMBUILD_EXTRA_OPTIONS} ${RPMBUILD_OPTIONS} "${SRPMS_DIR}/${SRCRPM}" || { [ "bashonfail" == "$BASH_ON_FAIL" ] && { echo "Build failed, spawning a shell" ; /bin/bash ; exit 1; } || exit 1 ; }
fi

echo "Done"


