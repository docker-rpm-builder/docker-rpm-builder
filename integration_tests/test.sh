#!/bin/bash
trap "{ echo ERROR detected; exit 1; }" ERR

LATEST_STARTED_TEST=""
function start_test {
    rm -rf tmux-src/*.tar.gz
    rm -rf ${RPM_DIR}
    echo "[$(date --rfc-3339=seconds)] TEST START: $1"
    LATEST_STARTED_TEST="$1"
}

function end_test {
    echo "[$(date --rfc-3339=seconds)] TEST DONE: ${LATEST_STARTED_TEST}"
    LATEST_STARTED_TEST=""
    rm -rf ${RPM_DIR}
}

RPM_DIR="/tmp/drb_rpms"
IMAGES="alanfranz/drb-epel-6-x86-64:latest alanfranz/drb-epel-5-x86-64:latest alanfranz/drb-epel-7-x86-64:latest"
for image in ${IMAGES}; do
    :
    start_test "without sources, build fails"
    docker-rpm-builder dir ${image} tmux-src/ ${RPM_DIR} && { echo "should have failed"; exit 1; }
    end_test

    start_test "with sources, two rpms (binary and debuginfo) are created"
    docker-rpm-builder dir ${image} tmux-src/ ${RPM_DIR} --download-sources --always-pull
    [ "$(ls ${RPM_DIR}/x86_64/tmux-* | wc -l)" == "2" ]
    end_test

    start_test "packages are not signed unless required"
    docker-rpm-builder dir ${image} tmux-src ${RPM_DIR} --download-sources
    [ "$(ls ${RPM_DIR}/x86_64/tmux-* | wc -l)" == "2" ]
    cp ./secret.pub ${RPM_DIR}
    docker run -v ${RPM_DIR}:${RPM_DIR} -w ${RPM_DIR}/x86_64 ${image} /bin/bash -c 'yum install -y rpmdevtools && rpm --import ../secret.pub && /usr/bin/rpmdev-checksig *.rpm' && { echo "should have failed"; exit 1; }
    end_test

    start_test "if I ask to sign, they get signed properly. Such signature can be verified."
    docker-rpm-builder dir ${image} tmux-src ${RPM_DIR} --download-sources --sign-with ./secret.pgp
    [ "$(ls ${RPM_DIR}/x86_64/tmux-* | wc -l)" == "2" ]
    cp ./secret.pub ${RPM_DIR}
    docker run -v ${RPM_DIR}:${RPM_DIR} -w ${RPM_DIR}/x86_64 ${image} /bin/bash -c 'yum install -y rpmdevtools && rpm --import ../secret.pub && /usr/bin/rpmdev-checksig *.rpm'
    end_test

    start_test "srcrpm building in ${image}"
    docker-rpm-builder srcrpm ${image} tmux-srcrpm/tmux-1.4-3.el5.1.src.rpm ${RPM_DIR}
    [ "$(ls ${RPM_DIR}/x86_64/tmux-* | wc -l)" == "2" ]
    end_test "srcrpm"
done

echo
echo "SUCCESS: all tests passed."

