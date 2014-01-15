### FIXME: Sysv script does not have condrestart option (redo sysv script)
### FIXME: amavisd-new requires clamd to run as user vscan, solution needed
### REMINDER: Look and sync with Petr Kristof's work

Summary: Anti-virus software
Name: clamav
Version: 0.98.1
Release: 1%{?dist}
License: GPLv2
Group: Applications/System
URL: http://www.clamav.net/

# Unfortunately, clamav includes support for RAR v3, derived from GPL
# incompatible unrar from RARlabs. We have to pull this code out. This
# tarball was created by
#   make clean-sources [TARBALL=<original-tarball>] [VERSION=<version>]
# Upstream: http://downloads.sourceforge.net/clamav/clamav-%{version}.tar.gz
Source0: clamav-%{version}-norar.tar.xz
Source1: clamav.init
Source2: clamav-milter.init
Source3: clamd-wrapper.tar.bz2

Source7: freshclam.cron
Source8: freshclam.logrotate
Source9: clamd.logrotate
Source10: clamav-milter.sysconfig

# To download the *.cvd, go to http://www.clamav.net and use the links
# there (I renamed the files to add the -version suffix for verifying).
Source11: http://db.local.clamav.net/main-55.cvd
Source12: http://db.local.clamav.net/daily-18353.cvd

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: bzip2-devel, zlib-devel, gmp-devel, curl-devel, xz, ncurses-devel
%{!?_without_milter:BuildRequires: sendmail-devel >= 8.12}
Requires: clamav-db = %{version}-%{release}
Requires(pre): shadow-utils

### Fedora Extras introduced them differently :(
Provides: libclamav
Obsoletes: libclamav < %{version}-%{release}
Provides: clamav-lib = %{version}-%{release}
Obsoletes: clamav-lib < %{version}-%{release}

%description
Clam AntiVirus is a GPL anti-virus toolkit for UNIX. The main purpose of
this software is the integration with mail servers (attachment scanning).
The package provides a flexible and scalable multi-threaded daemon, a
command line scanner, and a tool for automatic updating via Internet.

The programs are based on a shared library distributed with the Clam
AntiVirus package, which you can use with your own software. Most
importantly, the virus database is kept up to date

%package -n clamd
Summary: The Clam AntiVirus Daemon
Group: System Environment/Daemons
Requires: clamav = %{version}-%{release}

### Fedora Extras introduced them differently :(
Provides: clamav-server = %{version}-%{release}
Obsoletes: clamav-server < %{version}-%{release}
Provides: clamav-server-sysv = %{version}-%{release}
Obsoletes: clamav-server-sysv < %{version}-%{release}
Provides: clamav-scanner = %{version}-%{release}
Obsoletes: clamav-scanner < %{version}-%{release}
Provides: clamav-scanner-upstart = %{version}-%{release}
Obsoletes: clamav-scanner-upstart < %{version}-%{release}
Provides: clamav-server-sysvinit = %{version}-%{release}
Obsoletes: clamav-server-sysvinit < %{version}-%{release}


%description -n clamd
The Clam AntiVirus Daemon

%package milter
Summary: The Clam AntiVirus sendmail-milter Daemon
Group: Applications/System
Requires: clamd = %{version}-%{release}
Requires: /usr/sbin/sendmail
Provides: clamav-milter-sysv = %{version}-%{release}
Obsoletes: clamav-milter-sysv < %{version}-%{release}
Provides: clamav-milter-sysvinit = %{version}-%{release}
Obsoletes: clamav-milter-sysvinit < %{version}-%{release}

%description milter
The Clam AntiVirus sendmail-milter Daemon

%package db
Summary: Virus database for %{name}
Group: Applications/Databases
### Remove circular dependency
#Requires: clamav = %{version}-%{release}

### Fedora Extras introduced them differently :(
Provides: clamav-update = %{version}-%{release}
Obsoletes: clamav-update < %{version}-%{release}
Provides: clamav-data = %{version}-%{release}
Obsoletes: clamav-data < %{version}-%{release}
Obsoletes: clamav-data-empty <= %{version}-%{release}
# Ugly to put these in the db-package, but needed
# here to handle upgrades on EL5.
Provides: clamav-filesystem = %{version}-%{release}
Obsoletes: clamav-filesystem < %{version}-%{release}

%description db
The actual virus database for %{name}

%package devel
Summary: Header files, libraries and development documentation for %{name}
Group: Development/Libraries
Requires: clamav = %{version}-%{release}

### Fedora Extras introduced them differently :(
Obsoletes: libclamav-static-devel <= %{version}-%{release}
Obsoletes: libclamav-devel <= %{version}-%{release}
Provides: libclamav-static-devel, libclamav-devel

%description devel
This package contains the header files, static libraries and development
documentation for %{name}. If you like to develop programs using %{name},
you will need to install %{name}-devel.

%prep
# Handle that rpmbuild in RHEL < 6 doesn't handle xz archives automatically.
%setup -q -T -c
xz -dc %{SOURCE0} | (cd .. ; tar xvvf -)

%{__perl} -pi.orig -e 's|/lib\b|/%{_lib}|g;' configure

%{__perl} -pi.orig -e '
		s|\@DBDIR\@|\$(localstatedir)/lib/clamav|g;
		s|\@DBINST\@|\$(localstatedir)/lib/clamav|g;
		s|\@CFGDIR\@|\$(sysconfdir)|g;
		s|\@CFGINST\@|\$(sysconfdir)|g;
		s|^\@INSTALL_CLAMAV_CONF_TRUE\@|\t|g;
		s|^\@INSTALL_FRESHCLAM_CONF_TRUE\@|\t|g;
	' database/Makefile.in etc/Makefile.in

%{__perl} -pi.orig -e '
		s|^(Example)|#$1|;
		s|^#(LogFile) .+$|$1 %{_localstatedir}/log/clamav/clamd.log|;
		s|^#(LogFileMaxSize) .*|$1 0|;
		s|^#(LogTime)|$1|;
		s|^#(LogSyslog)|$1|;
		s|^#(PidFile) .+$|$1 %{_localstatedir}/run/clamav/clamd.pid|;
		s|^#(TemporaryDirectory) .+$|$1 %{_localstatedir}/tmp|;
		s|^#(DatabaseDirectory) .+$|$1 %{_localstatedir}/lib/clamav|;
		s|^#(LocalSocket) .+$|$1 %{_localstatedir}/run/clamav/clamd.sock|;
		s|^#(FixStaleSocket)|$1|;
		s|^#(TCPSocket) .+$|$1 3310|;
		s|^#(TCPAddr) .+$|$1 127.0.0.1|;
		s|^#(MaxConnectionQueueLength) .+$|$1 30|;
		s|^#(StreamSaveToDisk)|$1|;
		s|^#(MaxThreads) .+$|$1 50|;
		s|^#(ReadTimeout) .+$|$1 300|;
		s|^#(User) .+$|$1 clam|;
		s|^#(AllowSupplementaryGroups).*$|$1 yes|;
		s|^#(ScanPE) .+$|$1 yes|;
		s|^#(ScanELF) .+$|$1 yes|;
		s|^#(DetectBrokenExecutables)|$1|;
		s|^#(ScanOLE2) .+$|$1 yes|;
		s|^#(ScanMail)|$1|;
		s|^#(ScanArchive) .+$|$1 yes|;
		s|^#(ArchiveMaxCompressionRatio) .+|$1 300|;
		s|^#(ArchiveBlockEncrypted)|$1|;
		s|^#(ArchiveBlockMax)|$1|;
	' etc/clamd.conf.sample

%{__perl} -pi.orig -e '
		s|^(Example)|#$1|;
		s|^#(DatabaseDirectory) .+$|$1 %{_localstatedir}/lib/clamav|;
		s|^#(UpdateLogFile) .+$|$1 %{_localstatedir}/log/clamav/freshclam.log|;
		s|^#(LogSyslog)|$1|;
		s|^#(DatabaseOwner) .+$|$1 clam|;
		s|^(Checks) .+$|$1 24|;
	' etc/freshclam.conf.sample

%{__perl} -pi.orig -e '
		s|^(Example)|#$1|;
		s|^#(User) .+$|$1 clam|;
		s|^#(MilterSocket) inet.+$|$1 /var/run/clamav/clamav-milter.sock|;
		s|^#(PidFile) .+$|$1 /var/run/clamav/clamav-milter.pid|;
		s|^#(ClamdSocket) .+$|$1 unix:%{_localstatedir}/run/clamav/clamd.sock|;
	' etc/clamav-milter.conf.sample

%build
%configure  \
	--program-prefix="%{?_program_prefix}" \
%{!?_without_milter:--enable-milter} \
	--disable-clamav \
	--disable-static \
	--disable-zlib-vcheck \
	--disable-unrar \
	--enable-id-check \
	--enable-dns \
	--with-dbdir="%{_localstatedir}/lib/clamav" \
	--with-group="clam" \
	--with-libcurl \
	--with-user="clam" \
	--disable-llvm 

make %{?_smp_mflags}

%install
rm -rf %{buildroot}
make install DESTDIR="%{buildroot}"

install -Dp -m0755 %{SOURCE1} %{buildroot}%{_initrddir}/clamd
install -Dp -m0755 %{SOURCE7} %{buildroot}%{_sysconfdir}/cron.daily/freshclam
install -Dp -m0644 %{SOURCE8} %{buildroot}%{_sysconfdir}/logrotate.d/freshclam
install -Dp -m0644 %{SOURCE9} %{buildroot}%{_sysconfdir}/logrotate.d/clamav

mv -f %{buildroot}%{_sysconfdir}/clamd.conf{.sample,}
mv -f %{buildroot}%{_sysconfdir}/freshclam.conf{.sample,}

# now rewrite scripts and config files in-place
sed -i \
	-e 's!%%{_sbindir}!%{_sbindir}!g' \
	-e 's!%%{_bindir}!%{_bindir}!g' \
	-e 's!%%{_localstatedir}!%{_localstatedir}!g' \
	%{buildroot}%{_sysconfdir}/cron.daily/freshclam \
	%{buildroot}%{_sysconfdir}/logrotate.d/*

%if %{!?_without_milter:1}0
install -Dp -m0755 %{SOURCE2} %{buildroot}%{_initrddir}/clamav-milter
install -Dp -m0644 %{SOURCE10} %{buildroot}%{_sysconfdir}/sysconfig/clamav-milter
mv -f %{buildroot}%{_sysconfdir}/clamav-milter.conf{.sample,}
%else
rm %{buildroot}%{_mandir}/man8/clamav-milter.8*
%endif
# Install clamav-wrapper:
tar xjf %{SOURCE3} -C %{buildroot}/%{_prefix}/share

install -d -m0755 %{buildroot}%{_localstatedir}/log/clamav/
touch %{buildroot}%{_localstatedir}/log/clamav/freshclam.log
touch %{buildroot}%{_localstatedir}/log/clamav/clamd.log

install -d -m0755 %{buildroot}%{_localstatedir}/run/clamav/
install -d -m0755 %{buildroot}%{_sysconfdir}/clamd.d/

install -Dp -m0644 %{SOURCE11} %{buildroot}%{_localstatedir}/lib/clamav/main.cvd
install -Dp -m0644 %{SOURCE12} %{buildroot}%{_localstatedir}/lib/clamav/daily.cvd

# Clean up for later usage in documentation
for conf in etc/*.sample; do mv ${conf} ${conf%%.sample}; done

%post
/sbin/ldconfig

ZONES="/usr/share/zoneinfo/zone.tab"
CONFIG="/etc/sysconfig/clock"

if [ -r "$CONFIG" -a -r "$ZONES" ]; then
	source "$CONFIG"
	export CODE="$(grep -E "\b$ZONE\b" "$ZONES" | head -1 | cut -f1 | tr [A-Z] [a-z])"
fi

if [ -z "$CODE" ]; then
	export CODE="local"
fi

%{__perl} -pi -e '
		s|^(DatabaseMirror) database\.clamav\.net$|$1 db.$ENV{"CODE"}.clamav.net\n$1 db.local.clamav.net|;
		s|^(DatabaseMirror) db\.\.clamav\.net$|$1 db.$ENV{"CODE"}.clamav.net\n$1 db.local.clamav.net|;
	' %{_sysconfdir}/freshclam.conf{,.rpmnew} &>/dev/null || :

%postun -p /sbin/ldconfig

%pre
getent group clam >/dev/null || groupadd -r clam
getent passwd clam >/dev/null || \
useradd -r -g clam -d /var/lib/clamav -s /sbin/nologin \
    -c "Clam Anti Virus Checker" clam
exit 0

%pre -n clamd
getent group clam >/dev/null || groupadd -r clam
getent passwd clam >/dev/null || \
useradd -r -g clam -d /var/lib/clamav -s /sbin/nologin \
    -c "Clam Anti Virus Checker" clam
exit 0

%post -n clamd
/sbin/chkconfig --add clamd

%preun -n clamd
if [ $1 -eq 0 ]; then
	/sbin/service clamd stop &>/dev/null || :
	/sbin/chkconfig --del clamd
fi

%postun -n clamd
/sbin/service clamd condrestart &>/dev/null || :

%post milter
/sbin/chkconfig --add clamav-milter

%preun milter
if [ $1 -eq 0 ]; then
	/sbin/service clamav-milter stop &>/dev/null || :
	/sbin/chkconfig --del clamav-milter
fi

%postun milter
/sbin/service clamav-milter condrestart &>/dev/null || :

%pre db
getent group clam >/dev/null || groupadd -r clam
getent passwd clam >/dev/null || \
useradd -r -g clam -d /var/lib/clamav -s /sbin/nologin \
    -c "Clam Anti Virus Checker" clam
exit 0

%post db
# Remove old mirrors.dat, mostly because it will have the wrong
# owner after upgrading from clamav < 0.97:
test -f /var/lib/clamav/mirrors.dat && rm -f /var/lib/clamav/mirrors.dat
exit 0

%clean
rm -rf %{buildroot}

%files
%defattr(-, root, root, 0755)
%doc AUTHORS BUGS ChangeLog COPYING FAQ INSTALL NEWS README
%doc docs/*.pdf etc/freshclam.conf
%doc %{_mandir}/man1/sigtool.1*
%doc %{_mandir}/man1/clamscan.1*
%doc %{_mandir}/man1/freshclam.1*
%doc %{_mandir}/man5/freshclam.conf.5*
%config(noreplace) %{_sysconfdir}/freshclam.conf
%{_bindir}/clamscan
%{_bindir}/freshclam
%{_bindir}/sigtool
%{_bindir}/clambc
%{_libdir}/libclamav.so.*

%files -n clamd
%defattr(-, root, root, 0755)
%doc etc/clamd.conf
%doc %{_mandir}/man1/clamdscan.1*
%doc %{_mandir}/man1/clamconf.1*
%doc %{_mandir}/man1/clamdtop.1*
%doc %{_mandir}/man1/clambc.1*
%doc %{_mandir}/man5/clamd.conf.5*
%doc %{_mandir}/man8/clamd.8*
%doc %{_prefix}/share/clamav/README.clamd-wrapper
%{_prefix}/share/clamav/clamd-wrapper
%config(noreplace) %{_sysconfdir}/clamd.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/clamav
%{_sysconfdir}/clamd.d
%config %{_initrddir}/clamd
%{_sbindir}/clamd
%{_bindir}/clamconf
%{_bindir}/clamdscan
%{_bindir}/clamdtop

%defattr(0644, clam, clam, 0755)
%{_localstatedir}/run/clamav/
%dir %{_localstatedir}/lib/clamav/
%dir %{_localstatedir}/log/clamav/
%ghost %{_localstatedir}/log/clamav/clamd.log
%exclude %{_localstatedir}/lib/clamav/*

%if %{!?_without_milter:1}0
%files milter
%defattr(-, root, root, 0755)
%doc %{_mandir}/man5/clamav-milter.conf.5*
%doc %{_mandir}/man8/clamav-milter.8*
%config(noreplace) %{_sysconfdir}/sysconfig/clamav-milter
%config %{_initrddir}/clamav-milter
%{_sbindir}/clamav-milter
%config(noreplace) %{_sysconfdir}/clamav-milter.conf
%endif

%files db
%defattr(-, root, root, 0755)
%config(noreplace) %{_sysconfdir}/cron.daily/freshclam
%config(noreplace) %{_sysconfdir}/logrotate.d/freshclam

%defattr(0644, clam, clam, 0755)
%config(noreplace) %verify(user group mode) %{_localstatedir}/lib/clamav/
%dir %{_localstatedir}/log/clamav/
%ghost %{_localstatedir}/log/clamav/freshclam.log

%files devel
%defattr(-, root, root, 0755)
%{_bindir}/clamav-config
%{_includedir}/clamav.h
%{_libdir}/libclamav.so
%{_libdir}/pkgconfig/libclamav.pc
#%{_libdir}/libclamav.a
%exclude %{_libdir}/libclamav.la

%changelog
* Wed Jan 15 2014 Robert Scheck <robert@fedoraproject.org> - 0.98.1-1
- Upgrade to 0.98.1 and updated daily.cvd (#1053400)

* Sat Oct 19 2013 Robert Scheck <robert@fedoraproject.org> - 0.98-2
- Really fix all discrepancies between clamd initscript and clamd
  config file (#960923, thanks to John Horne)
- Ensure that a clamd and clamav-milter condrestart via initscript
  works (#1018312, thanks to Filippo Carletti)

* Sun Oct 06 2013 Robert Scheck <robert@fedoraproject.org> - 0.98-1
- Upgrade to 0.98 and updated main.cvd and daily.cvd (#1010168)
- Fixed discrepancies between clamd initscript and clamd config
  file (#960923, thanks to John Horne)
- Added build requirement to ncurses-devel for clamdtop (again)
- Moved clamd wrapper script and documentation into correct sub-
  package (#782596, thanks to Philip Prindeville)

* Tue Apr 23 2013 Orion Poplawski <orion@cora.nwra.com> - 0.97.8-1
- Upgrade to 0.97.8
- Updated daily.cvd

* Mon Mar 18 2013 Orion Poplawski <orion@cora.nwra.com> - 0.97.7-1
- Upgrade to 0.97.7

* Tue Sep 18 2012 Nick Bebout <nb@fedoraproject.org> - 0.97.6-1
- Upgrade to 0.97.6

* Wed Jun 20 2012 Nick Bebout <nb@fedoraproject.org> - 0.97.5-1
- Upgrade to 0.97.5
- Fix CVE-2012-1419 clamav: specially-crafted POSIX tar files evade detection
- Fix CVE-2012-1457 clamav: overly long length field in tar files evade detection
- Fix CVE-2012-1443 clamav: specially-crafted RAR files evade detection
- Fix CVE-2012-1458 clamav: specially-crafted CHM files evade detection
- Fix CVE-2012-1459 clamav: specially-crafted length field in tar files evade detection
- Ship local copy of virus database; it was removed by accident from 0.97.5 tarball

* Thu Jan 19 2012 Nick Bebout <nb@fedoraproject.org> - 0.97.3-4
- Split files out into SCM instead of in the spec

* Sun Jan 1 2012 Nick Bebout <nb@fedoraproject.org> - 0.97.3-3
- Revert patch from 0.97.3-2

* Tue Oct 18 2011 Nick Bebout <nb@fedoraproject.org> - 0.97.3-1
- Update to 0.97.3
- Fix CVE-2011-3627 clamav: Recursion level crash fixed in v0.97.3

* Thu Aug  4 2011 Jan-Frode Myklebuust <janfrode@tanso.net> - 0.97.2-5
- Configure MilterSocket, PidFile and MilterSocket in clamav-milter.conf.
  (bz#727894)

* Wed Jul 27 2011 Jan-Frode Myklebuust <janfrode@tanso.net> - 0.97.2-3
- include updated clamd-wrapper which get the PidFile setting from the
  service configuration file. 
- updated to 0.97.2
- Build-require xz
- CVE-2011-2721 Off-by-one error by scanning message hashes (#725694)

* Wed Jun 29 2011 Nick Bebout <nb@fedoraproject.org> - 0.97-14
- Require /usr/sbin/sendmail instead of sendmail

* Tue Apr 26 2011 Jan-Frode Myklebust <janfrode@tanso.net> - 0.97-13
- Obsolete and provide clamav-milter-sysvinit (bz#696856)

* Wed Mar 30 2011 Jan-Frode Myklebust <janfrode@tanso.net> - 0.97-12
- Move deletion of /var/lib/clamav/mirrors.dat to db package.
- Don't enable NotifyClamd in freshclam config and cronjob, as not
  everybody is running clamd. Running clamd's will anyway notice
  when db is updated.

* Fri Mar 18 2011 Jan-Frode Myklebust <janfrode@tanso.net> - 0.97-11
- Delete /var/lib/clamav/mirrors.dat, it will be recreated on first run.
- clamav-milter config cleanups.

* Wed Mar 16 2011 Jan-Frode Myklebust <janfrode@tanso.net> - 0.97-10
- Make sure /var/lib/clamav/mirrors.dat has owner fixed on upgrade.
- Don't start clamd or milter service by default.

* Tue Mar 15 2011 Jan-Frode Myklebust <janfrode@tanso.net> - 0.97-7
- rpm-provide all old package names that are now obsoleted

* Mon Mar 14 2011 Jan-Frode Myklebust <janfrode@tanso.net> - 0.97-6
- clam-db obsoletes old clamav-data-empty.

* Sun Mar 13 2011 Jan-Frode Myklebust <janfrode@tanso.net> - 0.97-4
- Add back clamd-wrapper to stay compatible with users
  of old packaging (amavisd-new).

* Wed Feb 23 2011 Nick Bebout <nb@fedoraproject.org> - 0.097-3
- Move db to /var/lib/clamav
- Ship empty directory /etc/clamd.d for amavisd-new

* Tue Feb 17 2011 Kevin Fenzi <kevin@tummy.com> - 0.97-2
- Disable llvm. 

* Tue Feb 08 2011 Kevin Fenzi <kevin@tummy.com> - 0.97-1
- Update to 0.97
- Fix up for current guidelines. 

* Fri Nov 23 2007 Kevin Fenzi <kevin@tummy.com> - 0.91.2-3
- Change username to get upgrades from fedora versions working. 

* Thu Nov 22 2007 Kevin Fenzi <kevin@tummy.com> - 0.91.2-2
- Initial changes for EPEL version. 

* Tue Aug 21 2007 Dag Wieers <dag@wieers.com> - 0.91.2-1
- Updated to release 0.91.2.

* Tue Jul 17 2007 Dag Wieers <dag@wieers.com> - 0.91.1-1
- Updated to release 0.91.1.

* Wed Jul 11 2007 Dag Wieers <dag@wieers.com> - 0.91-1
- Updated to release 0.91.

* Thu May 31 2007 Dag Wieers <dag@wieers.com> - 0.90.3-1
- Updated to release 0.90.3.

* Fri Apr 27 2007 Dag Wieers <dag@wieers.com> - 0.90.2-2
- Added clamav-milter support for EL2.1 now that it comes with a newer sendmail. (Tom G. Christensen)

* Sun Apr 15 2007 Dag Wieers <dag@wieers.com> - 0.90.2-1
- Updated to release 0.90.2.

* Fri Mar 09 2007 Dag Wieers <dag@wieers.com> - 0.90.1-4
- Removed circular dependency.

* Thu Mar 08 2007 Dag Wieers <dag@wieers.com> - 0.90.1-3
- Cleaned up default options to clamav-milter. (Adam T. Bowen)
- Removed -b/--bounce as it is no longer recognized. (Gerald Teschl)

* Mon Mar 05 2007 Dag Wieers <dag@wieers.com> - 0.90.1-2
- Removed the erroneous --dont-clean-log from the clamav-milter sysconfig. (Gerald Teschl)

* Fri Mar 02 2007 Dag Wieers <dag@wieers.com> - 0.90.1-1
- Updated to release 0.90.1.

* Tue Feb 20 2007 Dag Wieers <dag@wieers.com> - 0.90-3
- Do the right thing...

* Mon Feb 19 2007 Dag Wieers <dag@wieers.com> - 0.90-2
- The tarball was re-rolled before public release. Sigh.

* Tue Feb 13 2007 Dag Wieers <dag@wieers.com> - 0.90-1
- Updated to release 0.90.

* Tue Dec 12 2006 Dag Wieers <dag@wieers.com> - 0.88.7-1
- Updated to release 0.88.7.

* Sun Nov 05 2006 Dag Wieers <dag@wieers.com> - 0.88.6-1
- Updated to release 0.88.6.
- Added condrestart to sysv scripts. (Tsai Li Ming)

* Sat Oct 28 2006 Dag Wieers <dag@wieers.com> - 0.88.5-2
- Added missing clamav dependency to clamav-db.

* Sun Oct 15 2006 Dag Wieers <dag@wieers.com> - 0.88.5-1
- Updated to release 0.88.5.

* Mon Aug 07 2006 Dag Wieers <dag@wieers.com> - 0.88.4-1
- Updated to release 0.88.4.

* Mon Aug 07 2006 Dag Wieers <dag@wieers.com> - 0.88.3-2
- Incorporated UPX heap overflow fix.

* Sat Jul 01 2006 Dag Wieers <dag@wieers.com> - 0.88.3-1
- Updated to release 0.88.3.

* Sun Apr 30 2006 Dag Wieers <dag@wieers.com> - 0.88.2-1
- Updated to release 0.88.2.

* Tue Apr 04 2006 Dag Wieers <dag@wieers.com> - 0.88.1-1
- Updated to release 0.88.1.

* Mon Jan 09 2006 Dag Wieers <dag@wieers.com> - 0.88-1
- Updated to release 0.88.

* Sun Nov 13 2005 Dries Verachtert <dries@ulyssis.org> - 0.87.1-1
- Updated to release 0.87.1.

* Sat Sep 17 2005 Dag Wieers <dag@wieers.com> - 0.87-1
- Updated to release 0.87.

* Mon Jul 25 2005 Dag Wieers <dag@wieers.com> - 0.86.2-1
- Updated to release 0.86.2.

* Mon Jul 11 2005 Dag Wieers <dag@wieers.com> - 0.86.1-1
- Updated to release 0.86.1.

* Mon May 16 2005 Dag Wieers <dag@wieers.com> - 0.85.1-1
- Updated to release 0.85.1.

* Fri Apr 29 2005 Dag Wieers <dag@wieers.com> - 0.84-1
- Updated to release 0.84.

* Mon Feb 14 2005 Dag Wieers <dag@wieers.com> - 0.83-1
- Updated to release 0.83.

* Thu Feb 10 2005 Dag Wieers <dag@wieers.com> - 0.82-2
- Fix for false positive on RIFF files. (Roger Jochem)

* Mon Feb 07 2005 Dag Wieers <dag@wieers.com> - 0.82-1
- Updated to release 0.82.

* Thu Jan 27 2005 Dag Wieers <dag@wieers.com> - 0.81-1
- Improved logrotate scripts. (Filippo Grassilli)
- Updated to release 0.81.

* Wed Dec 01 2004 Dag Wieers <dag@wieers.com> - 0.80-2
- Added %%dir /var/clamav/log. (Adam Bowns)
- Changed logrotate script to use clamd.log. (Stuart Schneider)
- Added curl dependency. (Petr Kristof)
- Synchronized some options from Petr. (Petr Kristof)
- Fixed another clamav.conf reference. (Michael Best)

* Mon Nov 01 2004 Dag Wieers <dag@wieers.com> - 0.80-1
- Updated package description. (Arvin Troels)
- Incorporated fixes from Jima. (Jima)
- Config clamav.conf renamed to clamd.conf.
- Removed obsolete patch.
- Added macros for building without milter.
- Updated to release 0.80.

* Fri Jul 30 2004 Dag Wieers <dag@wieers.com> - 0.75.1-1
- Added obsoletes for fedora.us.
- Updated to release 0.75.1.

* Mon Jul 26 2004 Dag Wieers <dag@wieers.com> - 0.75-2
- Fixed a problem where $CODE was empty.

* Fri Jul 23 2004 Dag Wieers <dag@wieers.com> - 0.75-1
- Updated to release 0.75.

* Wed Jun 30 2004 Dag Wieers <dag@wieers.com> - 0.74-1
- Updated to release 0.74.

* Tue Jun 15 2004 Dag Wieers <dag@wieers.com> - 0.73-1
- Updated to release 0.73.

* Thu Jun 03 2004 Dag Wieers <dag@wieers.com> - 0.72-1
- Updated to release 0.72.

* Thu May 20 2004 Dag Wieers <dag@wieers.com> - 0.71-1
- Updated to release 0.71.

* Sun May 02 2004 Dag Wieers <dag@wieers.com> - 0.70-2
- Fixed the installation check for conf files. (Richard Soderberg, Udo Ruecker)
- Changed the init-order of the sysv scripts. (Will McCutcheon)
- Changes to the default configuration files.

* Sat Mar 17 2004 Dag Wieers <dag@wieers.com> - 0.70-1
- Updated to release 0.70.

* Tue Mar 16 2004 Dag Wieers <dag@wieers.com> - 0.68-1
- Updated to release 0.68.

* Fri Mar 12 2004 Dag Wieers <dag@wieers.com> - 0.67.1-1
- Updated to release 0.67-1.
- Added clamdwatch and trashcan to clamd.

* Mon Mar 08 2004 Dag Wieers <dag@wieers.com> - 0.67-1
- Personalized SPEC file.

* Mon Aug 22 2003 Matthias Saou/Che
- Added "--without milter" build option. (Matthias Saou)
- Fixed freshclam cron (Matthias Saou)
- Built the new package. (Che)

* Tue Jun 24 2003 Che
- clamav-milter introduced.
- a few more smaller fixes.

* Sun Jun 22 2003 Che
- version upgrade

* Mon Jun 16 2003 Che
- rh9 build
- various fixes
- got rid of rpm-helper prereq

* Fri Mar 24 2003 Che
- some cleanups and fixes
- new patch added

* Fri Nov 22 2002 Che
- fixed a config patch issue

* Fri Nov 22 2002 Che
- version upgrade and some fixes

* Sat Nov 02 2002 Che
- version upgrade

* Wed Oct 24 2002 Che
- some important changes for lsb compliance

* Wed Oct 23 2002 Che
- initial rpm release
