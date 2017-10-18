#!/bin/bash
set -e

EXIT_STATUS="FAIL"
CURRENT_SCRIPT="$(basename $0)"

. /dockerscripts/functions.sh

setup_cmd_log

log "Starting"

verify_environment_prereq
set_variables_from_environment

function finish {
  chown -R "${CALLING_UID}":"${CALLING_GID}" "${RPMS_DIR}" /tmp || /bin/true
  umount -f "${SOURCE_DIR}" || /bin/true
  log "Finished. Outcome: ${EXIT_STATUS}"
  [ "${EXIT_STATUS}" != "SUCCESS" ] && { log "**** FULL OUTPUT START ****" ; cat "${CMD_OUTPUT_FILENAME}" ; log "\n**** FULL OUTPUT END ****"; }
  rm -f "${CMD_OUTPUT_FILENAME}"
}
trap finish EXIT

setup_rpm_builddeps

TOMAP_DIR="${SOURCE_DIR}"
map_uid_gid_to_existing_users

setup_user_macros

SPEC="$(find "${SPECS_DIR}" -name '*.spec' | head -n 1)"

log "Now executing rpmbuild; this could take a while..."
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

if [ -r "/private.key" ]
then
    log "RPM signature enabled"
    setup_rpm_signing_system
	sign_rpmbuild_output_files
	log "RPM signature succeeded"
else
    log "RPM signature was not requested, output RPMs won't be signed"
fi

EXIT_STATUS="SUCCESS"
