#!/bin/bash
set -ex

function log {
    echo "[$(date --rfc-3339=seconds)] $*"
}

EXIT_STATUS="FAIL"

function finish {
  log "${0}: exiting. Outcome: ${EXIT_STATUS}"
}
trap finish EXIT

log "${0}: starting"
SPECS_DIR="$(rpm --eval %\{_specdir\})"
SPEC="$(ls "${SPECS_DIR}"/*.spec | head -n 1)"
yum-builddep -y --nogpgcheck "${SPEC}"

EXIT_STATUS="SUCCESS"
