#!/bin/bash
set -ex

[ -z "${CALLING_UID}" ] && { echo "Missing CALLING_UID"; /bin/false; }
[ -z "${CALLING_GID}" ] && { echo "Missing CALLING_GID"; /bin/false; }
[ -z "${BASH_ON_FAIL}" ] && { echo "Missing BASH_ON_FAIL. Won't drop into interactive shell if errors are found"; }
[ 0 -eq "${ENABLE_SOURCE_OVERLAY}" ] && { echo "Source overlay enabled"; }

RPMS_DIR=$(rpm --eval %{_rpmdir})
SRPMS_DIR=$(rpm --eval %{_srcrpmdir})
SOURCE_DIR=$(rpm --eval %{_sourcedir})
SPECS_DIR=$(rpm --eval %{_specdir})
ARCH=$(rpm --eval %{_arch})

function finish {
  chown -R ${CALLING_UID}:${CALLING_GID} ${RPMS_DIR} /tmp || /bin/true
  umount -f "${SOURCE_DIR}" || /bin/true
}
trap finish EXIT

if [ 0 -eq "${ENABLE_SOURCE_OVERLAY}" ]; then
    mkdir -p /tmp/upperdir /tmp/workdir
    mount -t overlay overlay -olowerdir="${SOURCE_DIR}",upperdir=/tmp/upperdir,workdir=/tmp/workdir "${SOURCE_DIR}"
fi

echo "starting $0"
SPEC=$(ls ${SPECS_DIR}/*.spec | head -n 1)
/dockerscripts/rpm-setup-deps.sh

#rpmbuild complains if it can't find a proper user for uid/gid of the source files;
#we should add all uid/gids for source files.
for gid in $(stat -c '%g' ${SOURCE_DIR}/*); do
    groupadd -g $gid "group$gid" >/dev/null 2>&1 || /bin/true
done

for uid in $(stat -c '%u' ${SOURCE_DIR}/*); do
    useradd -u $uid "user$uid" >/dev/null 2>&1 || /bin/true
done

if [ -r "/private.key" ]
then
    echo "Running with RPM signing"
    gpg --import /private.key
    [[ $(gpg --list-secret-keys) =~ uid(.*) ]]
    KEYNAME="${BASH_REMATCH[1]}"
    [ -n "${KEYNAME}" ] || { echo "could not find key for signing purpose"; exit 1; }
    echo -e "%_gpg_name ${KEYNAME}\n%_signature gpg" >> ${HOME}/.rpmmacros
	
	exitcode=0
    rpmbuild_out="$(rpmbuild ${RPMBUILD_EXTRA_OPTIONS} -bb $SPEC 2>&1)" || { exitcode="$?" ; /bin/true ; }
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
    echo -e "\n" | setsid rpmsign --addsign ${files} || { exitcode="$?" ; /bin/true ; }
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
    echo "Running without RPM signing"
    rpmbuild ${RPMBUILD_EXTRA_OPTIONS} -ba $SPEC || { [ "bashonfail" == "${BASH_ON_FAIL}" ] && { echo "Build failed, spawning a shell" ; /bin/bash ; exit 1; } || exit 1 ; }
fi
echo "Done"
