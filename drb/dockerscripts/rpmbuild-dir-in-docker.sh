#!/bin/bash
set -e

EXIT_STATUS="FAIL"

. /dockerscripts/functions

log "$(pwd)/${0}: starting"

verify_environment_prereq
set_variables_from_environment

function finish {
  chown -R "${CALLING_UID}":"${CALLING_GID}" "${RPMS_DIR}" /tmp || /bin/true
  umount -f "${SOURCE_DIR}" || /bin/true
  log "$(pwd)/${0}: exiting. Outcome: ${EXIT_STATUS}"
}
trap finish EXIT

setup_rpm_builddeps

TOMAP_DIR="${SOURCE_DIR}"
map_uid_gid_to_existing_users

if [ -r "/rpmmacros" ]
then
    cp /rpmmacros "${HOME}/.rpmmacros"
    echo -e "\n" >> "${HOME}/.rpmmacros"
fi

SPEC="$(ls "${SPECS_DIR}"/*.spec | head -n 1)"

if [ -r "/private.key" ]
then
    log "Running with RPM signing"
    GPGBIN="$(command -v gpg || command -v gpg2)"
    ${GPGBIN} --import /private.key
    [[ $(${GPGBIN} --list-secret-keys) =~ uid(.*) ]]
    KEYNAME="${BASH_REMATCH[1]}"
    [ -n "${KEYNAME}" ] || { log "could not find key for signing purpose"; exit 1; }
    echo -e "%_gpg_name ${KEYNAME}\n%_signature gpg" >> "${HOME}/.rpmmacros"
    ${GPGBIN} --armor --export "${KEYNAME}" > /tmp/public.gpg
    rpm --import /tmp/public.gpg
	
	exitcode=0
    rpmbuild_out="$(rpmbuild ${RPMBUILD_EXTRA_OPTIONS} -bb "$SPEC" 2>&1)" || { exitcode="$?" ; /bin/true ; }
    if [ "${exitcode}" -ne 0 ]; then
			if [ "bashonfail" == "${BASH_ON_FAIL}" ]; then
				# if the build is interactive, we can see what's printed in the current log, no need to reprint.
				log "Build failed, spawning a shell. The build will terminate after such shell is closed."
				/bin/bash
			else 
				log "rpmbuild command failed:output is: -->\n${rpmbuild_out}\nrpmbuild command output end\n\n."
			fi
		exit ${exitcode}
	fi
    
	files="$(sed -n -e '/Checking for unpackaged file/,$p' <<< "${rpmbuild_out}" | grep 'Wrote:' | cut -d ':' -f 2)"
	
	exitcode=0
    echo -e "\n" | setsid rpmsign --addsign ${files} ||  /bin/true
    rpm -K ${files} | grep -e "pgp" -e "OK" || { log "Signing failed." ; exitcode=1 ; }
    if [ "${exitcode}" -ne 0 ]; then
			if [ "bashonfail" == "${BASH_ON_FAIL}" ]; then
				# if the build is interactive, we can see what's printed in the current log, no need to reprint.
				log "Signing failed, spawning a shell. The build will terminate after such shell is closed."
				/bin/bash
			else
				log "rpmsign command failed:output is: -->\n${rpmbuild_out}\nrpmsign command output end\n\n."
			fi
		# don't accidentally retain unsigned files
		rm -f "${files}"
		exit "${exitcode}"
	fi
else
    log "Running without RPM signing"
    rpmbuild ${RPMBUILD_EXTRA_OPTIONS} -bb "$SPEC" || { [ "bashonfail" == "${BASH_ON_FAIL}" ] && { log "Build failed, spawning a shell" ; /bin/bash ; exit 1; } || exit 1 ; }
fi

EXIT_STATUS="SUCCESS"
