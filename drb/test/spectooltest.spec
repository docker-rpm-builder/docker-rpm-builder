Name:           tmux
Version:        1.6
Release:        3%{?dist}
Summary:        A terminal multiplexer
Group:          Applications/System
License:        ISC and BSD
URL:            http://sourceforge.net/projects/tmux
Source0:        https://raw.githubusercontent.com/alanfranz/docker-rpm-builder/master/README.md 
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  ncurses-devel
BuildRequires:  libevent-devel

