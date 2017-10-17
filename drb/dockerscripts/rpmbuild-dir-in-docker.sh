#!/bin/bash
set -e

EXIT_STATUS="FAIL"
CURRENT_SCRIPT="$(pwd)/$(basename $0)"

. /dockerscripts/functions

log "Starting"

verify_environment_prereq
set_variables_from_environment

function finish {
  chown -R "${CALLING_UID}":"${CALLING_GID}" "${RPMS_DIR}" /tmp || /bin/true
  umount -f "${SOURCE_DIR}" || /bin/true
  log "Finished. Outcome: ${EXIT_STATUS}"
}
trap finish EXIT

setup_rpm_builddeps

TOMAP_DIR="${SOURCE_DIR}"
map_uid_gid_to_existing_users

setup_user_macros

SPEC="$(find "${SPECS_DIR}" -name '*.spec' | head -n 1)"

log "spec is ${SPEC}"

if [ -r "/private.key" ]
then
    setup_rpm_signing_system

	log "rpmbuild now starting"
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
	log "rpmbuild succeeded"

	sign_rpmbuild_output_files
else
    log "Running without RPM signing"
    log "rpmbuild now starting"
    rpmbuild ${RPMBUILD_EXTRA_OPTIONS} -bb "$SPEC" || { [ "bashonfail" == "${BASH_ON_FAIL}" ] && { log "Build failed, spawning a shell" ; /bin/bash ; exit 1; } || exit 1 ; }
    log "rpmbuild succeeded"
fi

EXIT_STATUS="SUCCESS"
