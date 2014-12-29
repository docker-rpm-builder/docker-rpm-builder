#!/bin/bash
trap "{ echo ERROR detected; exit 1; }" ERR

LATEST_STARTED_TEST=""
function start_test {
    echo "[$(date --rfc-3339=seconds)] TEST START: $1"
    LATEST_STARTED_TEST="$1"
}

function end_test {
    echo "[$(date --rfc-3339=seconds)] TEST DONE: ${LATEST_STARTED_TEST}"
    LATEST_STARTED_TEST=""
    rm -rf ${RPM_DIR}
}


#EPEL6_IMAGE="alanfranz/drb-epel-6-x86-64:latest"
EPEL6_IMAGE="epel6dev"
RPM_DIR="/tmp/drb_rpms"
rm -rf tmux-src/*.tar.gz
rm -rf ${RPM_DIR}

start_test "without sources, build fails"
docker-rpm-builder dir ${EPEL6_IMAGE} tmux-src/ ${RPM_DIR} && { echo "should have failed"; exit 1; }
end_test

start_test "with sources, two rpms (binary and debuginfo) are created"
docker-rpm-builder dir --download-sources ${EPEL6_IMAGE} tmux-src/ ${RPM_DIR}
[ "$(ls ${RPM_DIR}/x86_64/tmux-* | wc -l)" == "2" ]
end_test

start_test "packages are not signed unless required"
docker-rpm-builder dir ${EPEL6_IMAGE} tmux-src ${RPM_DIR} --download-sources
cp ./secret.pub ${RPM_DIR}
docker run -v ${RPM_DIR}:${RPM_DIR} -w ${RPM_DIR}/x86_64 ${EPEL6_IMAGE} /bin/bash -c 'yum install -y rpmdevtools && rpm --import ../secret.pub && /usr/bin/rpmdev-checksig *.rpm' && { echo "should have failed"; exit 1; }
end_test

start_test "if I ask to sign, they get signed properly. Such signature can be verified."
docker-rpm-builder dir ${EPEL6_IMAGE} tmux-src ${RPM_DIR} --download-sources --sign-with ./secret.pgp
cp ./secret.pub ${RPM_DIR}
docker run -v ${RPM_DIR}:${RPM_DIR} -w ${RPM_DIR}/x86_64 ${EPEL6_IMAGE} /bin/bash -c 'yum install -y rpmdevtools && rpm --import ../secret.pub && /usr/bin/rpmdev-checksig *.rpm'
end_test

