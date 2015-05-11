#!/bin/bash
install_dir="/opt/docker-rpm-builder"

set -e
[ -n "$1" ]
DRB_VERSION="$1"
apt-get -y update
apt-get -y dist-upgrade
apt-get -y install python python-setuptools python-virtualenv ruby ruby-dev rubygems-integration build-essential libffi-dev
gem install fpm -v 1.3.3
easy_install pipsi
mkdir -p ${install_dir}/{bin,env}
pipsi --home ${install_dir}/env --bin-dir ${install_dir}/bin install --python /usr/bin/python "docker-rpm-builder==${DRB_VERSION}"
cd /usr/bin
ln -s /opt/docker-rpm-builder/bin/docker-rpm-builder .
cd /
tar czvf drb.tar.gz /opt/docker-rpm-builder /usr/bin/docker-rpm-builder
cd /host
fpm -s tar -t deb --name "docker-rpm-builder" --after-install after-install.sh  --version ${DRB_VERSION} --depends "lxc-docker >= 1.3" --depends "wget" ../drb.tar.gz 
chmod 666 *.deb
