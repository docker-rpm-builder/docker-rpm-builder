#!/bin/bash
set -e
SRCRPM=$1
yum-builddep --nogpgcheck -y ${SRCRPM}
rpmbuild --rebuild ${SRCRPM}
