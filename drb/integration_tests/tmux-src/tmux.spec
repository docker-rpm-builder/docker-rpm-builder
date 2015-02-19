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

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jan 31 2012 Sven Lankes <sven@lank.es> 1.6-1
- New upstream release

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Nov 01 2011 Sven Lankes <sven@lank.es> 1.5-1
- New upstream release
- Do the right thing (tm) and revert to $upstream-behaviour: 
   No longer install tmux setgid and no longer use /var/run/tmux 
   for sockets. Use "tmux -S /var/run/tmux/tmux-`id -u`/default attach"
   if you need to access an "old" tmux session
- tmux can be used as a login shell so add it to /etc/shells

* Sat Apr 16 2011 Sven Lankes <sven@lank.es> 1.4-4
- Add /var/run/tmp to tmpdir.d - fixes rhbz 656704 and 697134

* Sun Apr 10 2011 Sven Lankes <sven@lank.es> 1.4-3
- Fix CVE-2011-1496
- Fixes rhbz #693824

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Dec 28 2010 Filipe Rosset <rosset.filipe@gmail.com> 1.4-1
- New upstream release

* Fri Aug 06 2010 Filipe Rosset <filiperosset@fedoraproject.org> 1.3-2
- Rebuild for F-13

* Mon Jul 19 2010 Sven Lankes <sven@lank.es> 1.3-1
- New upstream release

* Sun Mar 28 2010 Sven Lankes <sven@lank.es> 1.2-1
- New upstream release
- rediff writehard patch

* Mon Nov 09 2009 Sven Lankes <sven@lank.es> 1.1-1
- New upstream release

* Sun Nov 01 2009 Sven Lankes <sven@lank.es> 1.0-2
- Add debian patches
- Add tmux group for improved socket handling

* Sat Oct 24 2009 Sven Lankes <sven@lank.es> 1.0-1
- New upstream release

* Mon Jul 13 2009 Chess Griffin <chess@chessgriffin.com> 0.9-1
- Update to version 0.9.
- Remove sed invocation as this was adopted upstream.
- Remove optflags patch since upstream source now uses ./configure and
  detects the flags when passed to make.

* Tue Jun 23 2009 Chess Griffin <chess@chessgriffin.com> 0.8-5
- Note that souce is mostly ISC licensed with some 2 and 3 clause BSD in
  compat/.
- Remove fixiquote.patch and instead use a sed invocation in setup.

* Mon Jun 22 2009 Chess Griffin <chess@chessgriffin.com> 0.8-4
- Add optimization flags by patching GNUmakefile and passing LDFLAGS
  to make command.
- Use consistent macro format.
- Change examples/* to examples/ and add TODO to docs.

* Sun Jun 21 2009 Chess Griffin <chess@chessgriffin.com> 0.8-3
- Remove fixperms.patch and instead pass them at make install stage.

* Sat Jun 20 2009 Chess Griffin <chess@chessgriffin.com> 0.8-2
- Fix Source0 URL to point to correct upstream source.
- Modify fixperms.patch to set 644 permissions on the tmux.1.gz man page.
- Remove wildcards from 'files' section and replace with specific paths and
  filenames.

* Mon Jun 15 2009 Chess Griffin <chess@chessgriffin.com> 0.8-1
- Initial RPM release.
