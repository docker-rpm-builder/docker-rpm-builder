FROM centos
MAINTAINER Alan Franzoni username@franzoni.eu
RUN yum install -y rpm-build rpmdevtools yum-utils make gcc
