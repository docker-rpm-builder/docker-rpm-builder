#!/bin/bash
set -x
shopt -s expand_aliases
RPM_DIR=$(mktemp -d ${HOME}/drb-test-tmp-rpm.XXXXXX)
SRC_DIR=$(mktemp -d ${HOME}/drb-test-tmp-src.XXXXXX)
trap "{ echo ERROR detected; rm -rf ${RPM_DIR} ${SRC_DIR} ; exit 1; }" ERR
[ -n "$DRB_EXEC" ] && alias docker-rpm-builder="${DRB_EXEC}"
echo "Testing $(type docker-rpm-builder)"
IMAGES=${1:-alanfranz/drb-epel-6-x86-64:latest alanfranz/drb-epel-5-x86-64:latest alanfranz/drb-epel-7-x86-64:latest alanfranz/drb-fedora-20-x86-64:latest alanfranz/drb-fedora-21-x86-64:latest alanfranz/drb-fedora-22-x86-64:latest}



LATEST_STARTED_TEST=""
function start_test {
    rm -rf tmux-src/*.tar.gz
    rm -rf ${RPM_DIR}
    rm -rf ${SRC_DIR}
    mkdir -p ${SRC_DIR}
    echo "[$(date)] TEST START: $1"
    LATEST_STARTED_TEST="$1"
}

function end_test {
    echo "[$(date)] TEST DONE: ${LATEST_STARTED_TEST}"
    LATEST_STARTED_TEST=""
    rm -rf ${RPM_DIR}
    rm -rf ${SRC_DIR}
}

for image in ${IMAGES}; do
    start_test "spectemplate variables are substituted"
    cp -r tmux-src-template/* ${SRC_DIR}
    ARBITRARY_PARAMETER=arbitraryparameter docker-rpm-builder dir ${image} ${SRC_DIR} ${RPM_DIR} --download-sources --always-pull
    [ "$(ls ${RPM_DIR}/x86_64/tmux-*arbitraryparameter* | wc -l)" == "2" ]
    end_test

    start_test "without sources, build fails"
    cp -r tmux-src/* ${SRC_DIR}
    docker-rpm-builder dir ${image} ${SRC_DIR} ${RPM_DIR} && { echo "should have failed"; exit 1; }
    end_test

    start_test "with sources, two rpms (binary and debuginfo) are created"
    cp -r tmux-src/* ${SRC_DIR}
    docker-rpm-builder dir ${image} ${SRC_DIR} ${RPM_DIR} --download-sources --always-pull
    [ "$(ls ${RPM_DIR}/x86_64/tmux-* | wc -l)" == "2" ]
    end_test


    start_test "created binaries have the ownership that is passed"
    cp -r tmux-src/* ${SRC_DIR}
    MY_ID=$(id -u)
    docker-rpm-builder dir ${image} ${SRC_DIR} ${RPM_DIR} --download-sources --always-pull --target-ownership ${MY_ID}:1234
    [ "$(stat -c '%u:%g' ${RPM_DIR}/x86_64/tmux-*)" == "${MY_ID}:1234"$'\n'"${MY_ID}:1234" ]
    end_test

    start_test "packages are not signed unless required"
    cp -r tmux-src/* ${SRC_DIR}
    docker-rpm-builder dir ${image} ${SRC_DIR} ${RPM_DIR} --download-sources
    [ "$(ls ${RPM_DIR}/x86_64/tmux-* | wc -l)" == "2" ]
    cp ./secret.pub ${RPM_DIR}
    docker run -v ${RPM_DIR}:${RPM_DIR} -w ${RPM_DIR}/x86_64 ${image} /bin/bash -c 'yum install -y rpmdevtools && rpm --import ../secret.pub && /usr/bin/rpmdev-checksig *.rpm' && { echo "should have failed"; exit 1; }
    end_test

    start_test "if I ask to sign, they get signed properly. Such signature can be verified."
    cp -r tmux-src/* ${SRC_DIR}
    docker-rpm-builder dir ${image} ${SRC_DIR} ${RPM_DIR} --download-sources --sign-with ./secret.pgp
    [ "$(ls ${RPM_DIR}/x86_64/tmux-* | wc -l)" == "2" ]
    cp ./secret.pub ${RPM_DIR}
    docker run -v ${RPM_DIR}:${RPM_DIR} -w ${RPM_DIR}/x86_64 ${image} /bin/bash -c 'yum install -y rpmdevtools && rpm --import ../secret.pub && /usr/bin/rpmdev-checksig *.rpm'
    end_test


    start_test "signed srcrpm building"
    docker-rpm-builder srcrpm ${image} tmux-srcrpm/tmux-1.4-3.el5.1.src.rpm ${RPM_DIR} --sign-with ./secret.pgp
    [ "$(ls ${RPM_DIR}/x86_64/tmux-* | wc -l)" == "2" ]
    cp ./secret.pub ${RPM_DIR}
    docker run -v ${RPM_DIR}:${RPM_DIR} -w ${RPM_DIR}/x86_64 ${image} /bin/bash -c 'yum install -y rpmdevtools && rpm --import ../secret.pub && /usr/bin/rpmdev-checksig *.rpm'
    end_test

    start_test "srcrpm building in ${image}"
    docker-rpm-builder srcrpm ${image} tmux-srcrpm/tmux-1.4-3.el5.1.src.rpm ${RPM_DIR}
    [ "$(ls ${RPM_DIR}/x86_64/tmux-* | wc -l)" == "2" ]
    end_test

    start_test "srcrpm building in ${image} with ownership change"
    MY_ID=$(id -u)
    docker-rpm-builder srcrpm ${image} tmux-srcrpm/tmux-1.4-3.el5.1.src.rpm ${RPM_DIR} --target-ownership ${MY_ID}:1234
    [ "$(stat -c '%u:%g' ${RPM_DIR}/x86_64/tmux-*)" == "${MY_ID}:1234"$'\n'"${MY_ID}:1234" ]
    end_test

done

echo
echo "SUCCESS: all tests passed."

