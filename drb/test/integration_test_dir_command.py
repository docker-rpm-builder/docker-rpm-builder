from drb.spawn import SpawnedProcessError
from unittest2 import TestCase
from click.testing import CliRunner
import os

from drb.tempdir import TempDir
from drb.commands.dir import dir

REFERENCE_IMAGE = "alanfranz/drb-epel-7-x86-64:latest"

class TestDirCommand(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.src = TempDir.platformwise()
        self.rpm = TempDir.platformwise()

    def tearDown(self):
        self.src.delete()
        self.rpm.delete()


    def test_dir_command_fails_if_sources_unavailable_and_downloadsources_not_enabled(self):
        with open(os.path.join(self.src.path, "tmux.spec"), "wb") as f:
            f.write(TMUX_SPEC)

        self.assertRaises(SpawnedProcessError, self.runner.invoke, dir, [REFERENCE_IMAGE, self.src.path, self.rpm.path],
                          catch_exceptions=False)

    def test_dir_command_produces_binary_rpm_and_debuginfo_packages_if_valid_spec_passed_and_downloadsources_enabled(self):
        with open(os.path.join(self.src.path, "tmux.spec"), "wb") as f:
            f.write(TMUX_SPEC)

        self.runner.invoke( dir, [REFERENCE_IMAGE, self.src.path, self.rpm.path, "--download-sources"],  catch_exceptions=False)
        self.assertEquals(2, len(os.listdir(os.path.join(self.rpm.path, "x86_64"))))






TMUX_SPEC = """
Name:           tmux
Version:        1.6
Release:        3%{?dist}
Summary:        A terminal multiplexer

Group:          Applications/System
# Most of the source is ISC licensed; some of the files in compat/ are 2 and
# 3 clause BSD licensed.
License:        ISC and BSD
URL:            http://sourceforge.net/projects/tmux
Source0:        http://pkgs.fedoraproject.org/repo/pkgs/tmux/tmux-1.6.tar.gz/3e37db24aa596bf108a0442a81c845b3/tmux-1.6.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  ncurses-devel
BuildRequires:  libevent-devel

%description
tmux is a "terminal multiplexer."  It enables a number of terminals (or
windows) to be accessed and controlled from a single terminal.  tmux is
intended to be a simple, modern, BSD-licensed alternative to programs such
as GNU Screen.

%prep
%setup -q

%build
%configure
make %{?_smp_mflags} LDFLAGS="%{optflags}"

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} INSTALLBIN="install -p -m 755" INSTALLMAN="install -p -m 644"

%clean
rm -rf %{buildroot}

%post
if [ ! -f %{_sysconfdir}/shells ] ; then
    echo "%{_bindir}/tmux" > %{_sysconfdir}/shells
else
    grep -q "^%{_bindir}/tmux$" %{_sysconfdir}/shells || echo "%{_bindir}/tmux" >> %{_sysconfdir}/shells
fi

%postun
if [ $1 -eq 0 ] && [ -f %{_sysconfdir}/shells ]; then
    sed -i '\!^%{_bindir}/tmux$!d' %{_sysconfdir}/shells
fi

%files
%defattr(-,root,root,-)
%doc CHANGES FAQ NOTES TODO examples/
%{_bindir}/tmux
%{_mandir}/man1/tmux.1.*

%changelog
* Fri Aug 09 2013 Steven Roberts <strobert@strobe.net> - 1.6-3
- Building for el6
- Remove tmux from the shells file upon package removal (RH bug #972633)
"""

