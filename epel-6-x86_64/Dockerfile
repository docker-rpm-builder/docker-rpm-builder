FROM centos:6.4
MAINTAINER Alan
ADD files/etc/yum.conf /etc/
RUN yum groupinstall -y buildsys-build
RUN yum install -y yum-utils
RUN useradd -s /sbin/nologin mockbuild
