#global snapshot	rc1

## Fedora Extras specific customization below...
%bcond_without       	fedora
%bcond_with		unrar
##

%global username	clamav
%global homedir		%_var/lib/clamav
%global freshclamlog	%_var/log/freshclam.log
%global milterlog	%_var/log/clamd.milter
%global milteruser	clamilt
%global milterstatedir	%_var/run/clamav-milter
%global pkgdatadir	%_datadir/%name


%{!?release_func:%global release_func() %1%{?dist}}

Summary:	End-user tools for the Clam Antivirus scanner
Name:		clamav
Version:	0.94
Release:	%release_func 1%{?snapshot:.%snapshot}

License:	%{?with_unrar:proprietary}%{!?with_unrar:GPLv2}
Group:		Applications/File
URL:		http://www.clamav.net
%if 0%{?with_unrar:1}
Source0:	http://download.sourceforge.net/sourceforge/clamav/%name-%version%{?snapshot}.tar.gz
Source999:	http://download.sourceforge.net/sourceforge/clamav/%name-%version%{?snapshot}.tar.gz.sig
%else
# Unfortunately, clamav includes support for RAR v3, derived from GPL 
# incompatible unrar from RARlabs. We have to pull this code out.
# tarball was created by
#   make clean-sources [TARBALL=<original-tarball>] [VERSION=<version>]
Source0:	%name-%version%{?snapshot}-norar.tar.bz2
%endif
Source1:	clamd-wrapper
Source2:	clamd.sysconfig
Source3:	clamd.logrotate
Source5:	clamd-README
Source6:	clamav-update.logrotate
Source7:	clamd.SERVICE.init
Source8:	clamav-notify-servers
Patch21:	clamav-0.93.1-path.patch
Patch22:	clamav-0.93.3-initoff.patch
Patch24:	clamav-0.92-private.patch
Patch25:	clamav-0.92-open.patch
Patch26:	clamav-0.93.3-pid.patch
BuildRoot:	%_tmppath/%name-%version-%release-root
Requires:	clamav-lib = %version-%release
Requires:	data(clamav)
BuildRequires:	zlib-devel bzip2-devel gmp-devel curl-devel
BuildRequires:	%_includedir/tcpd.h
BuildRequires:	bc

%package filesystem
Summary:	Filesystem structure for clamav
Group:		Applications/File
Provides:	user(clamav)
Provides:	group(clamav)
# Prevent version mix
Conflicts:	%name < %version-%release
Conflicts:	%name > %version-%release
BuildRequires:	fedora-usermgmt-devel
%{?FE_USERADD_REQ}

%package lib
Summary:	Dynamic libraries for the Clam Antivirus scanner
Group:		System Environment/Libraries
Requires:	data(clamav)

%package devel
Summary:	Header files and libraries for the Clam Antivirus scanner
Group:		Development/Libraries
Source100:	clamd-gen
Requires:	clamav-lib        = %version-%release
Requires:	clamav-filesystem = %version-%release
Requires(pre):	%_libdir/pkgconfig
Requires:	pkgconfig

%package data
Summary:	Virus signature data for the Clam Antivirus scanner
Group:		Applications/File
Requires(pre):		clamav-filesystem = %version-%release
Requires(postun):	clamav-filesystem = %version-%release
Provides:		data(clamav) = full
Conflicts:		data(clamav) < full
Conflicts:		data(clamav) > full

%package data-empty
Summary:	Empty data package for the Clam Antivirus scanner
Group:		Applications/File
Provides:	data(clamav) = empty
Conflicts:	data(clamav) < empty
Conflicts:	data(clamav) > empty

%package update
Summary:	Auto-updater for the Clam Antivirus scanner data-files
Group:		Applications/File
Source200:	freshclam-sleep
Source201:	freshclam.sysconfig
Source202:	clamav-update.cron
Requires:		clamav-filesystem = %version-%release
Requires(pre):		/etc/cron.d
Requires(postun):	/etc/cron.d
Requires(post):		%__chown %__chmod
Requires(post):		group(clamav)

%package server
Summary:	Clam Antivirus scanner server
Group:		System Environment/Daemons
Requires:	init(clamav-server)
Requires:	data(clamav)
Requires:	clamav-filesystem = %version-%release
Requires:	clamav-lib        = %version-%release

%package server-sysv
Summary:	SysV initscripts for clamav server
Group:		System Environment/Daemons
Provides:	init(clamav-server) = sysv
Requires:	clamav-server = %version-%release
Requires(pre):		%_initrddir
Requires(postun):	%_initrddir

%package milter
Summary:	Milter module for the Clam Antivirus scanner
Group:		System Environment/Daemons
Requires:	clamav-milter-core = %version-%release
Requires:	milter(clamav)

%package milter-core
Summary:	Core milter module for the Clam Antivirus scanner
Group:		System Environment/Daemons
Requires:	init(clamav-milter)
BuildRequires:	sendmail-devel
BuildRequires:	fedora-usermgmt-devel
Provides:	user(%milteruser)
Provides:	group(%milteruser)
Requires(post):	coreutils
%{?FE_USERADD_REQ}

%package milter-sendmail
Summary:	Sendmail customizations for clamav-milter
Group:		System Environment/Daemons
Source300:	README.fedora
Requires:	sendmail
Requires:	clamav-milter-core = %version-%release
Requires(pre):	user(%milteruser)
Requires(pre):	group(%milteruser)
Provides:	milter(clamav) = sendmail
Conflicts:	milter(clamav) < sendmail
Conflicts:	milter(clamav) > sendmail

%package milter-sysv
Summary:	SysV initscripts for the clamav sendmail-milter
Group:		System Environment/Daemons
Provides:	init(clamav-milter) = sysv
Requires:	clamav-milter = %version-%release
Requires(post):		user(%milteruser) clamav-milter
Requires(preun):	user(%milteruser) clamav-milter
Requires(pre):		%_initrddir
Requires(postun):	%_initrddir initscripts
Requires(post):		chkconfig
Requires(preun):	chkconfig initscripts


%description
Clam AntiVirus is an anti-virus toolkit for UNIX. The main purpose of this
software is the integration with mail servers (attachment scanning). The
package provides a flexible and scalable multi-threaded daemon, a command
line scanner, and a tool for automatic updating via Internet. The programs
are based on a shared library distributed with the Clam AntiVirus package,
which you can use with your own software. The virus database is based on
the virus database from OpenAntiVirus, but contains additional signatures
(including signatures for popular polymorphic viruses, too) and is KEPT UP
TO DATE.

%description filesystem
This package provides the filesystem structure and contains the
user-creation scripts required by clamav.

%description lib
This package contains dynamic libraries shared between applications
using the Clam Antivirus scanner.

%description devel
This package contains headerfiles and libraries which are needed to
build applications using clamav.

%description data
This package contains the virus-database needed by clamav. This
database should be updated regularly; the 'clamav-update' package
ships a corresponding cron-job. This package and the
'clamav-data-empty' package are mutually exclusive.

Use -data when you want a working (but perhaps outdated) virus scanner
immediately after package installation.

Use -data-empty when you are updating the virus database regulary and
do not want to download a >5MB sized rpm-package with outdated virus
definitions.


%description data-empty
This is an empty package to fulfill inter-package dependencies of the
clamav suite. This package and the 'clamav-data' package are mutually
exclusive.

Use -data when you want a working (but perhaps outdated) virus scanner
immediately after package installation.

Use -data-empty when you are updating the virus database regulary and
do not want to download a >5MB sized rpm-package with outdated virus
definitions.


%description update
This package contains programs which can be used to update the clamav
anti-virus database automatically. It uses the freshclam(1) utility for
this task. To activate it, uncomment the entry in /etc/cron.d/clamav-update.

%description server
ATTENTION: most users do not need this package; the main package has
everything (or depends on it) which is needed to scan for virii on
workstations.

This package contains files which are needed to execute the clamd-daemon.
This daemon does not provide a system-wide service. Instead of, an instance
of this daemon should be started for each service requiring it.

See the README file how this can be done with a minimum of effort.


%description server-sysv
SysV initscripts template for the clamav server


%description milter
This package contains files which are needed to run the clamav-milter.

%description milter-sysv
The SysV initscripts for clamav-milter.

%description milter-core
Core files for the clamav-milter.

%description milter-sendmail
Sendmail customizations of the clamav-milter.


## ------------------------------------------------------------

%prep
%setup -q -n %{name}-%{version}%{?snapshot}

%patch21 -p1 -b .path
%patch22 -p1 -b .initoff
%patch24 -p1 -b .private
%patch25 -p1 -b .open
%patch26 -p1 -b .pid

install -p -m0644 %SOURCE300 clamav-milter/

mkdir -p libclamunrar{,_iface}
%{!?with_unrar:touch libclamunrar/{Makefile.in,all,install}}

perl -pi -e 's!^(#?LogFile ).*!\1/var/log/clamd.<SERVICE>!g;
	     s!^#?(LocalSocket ).*!\1/var/run/clamd.<SERVICE>/clamd.sock!g;
	     s!^#?(PidFile ).*!\1/var/run/clamd.<SERVICE>/clamd.pid!g;
	     s!^#?(User ).*!\1<USER>!g;
             s! /usr/local/share/clamav,! %homedir,!g;
            ' etc/clamd.conf

perl -pi -e 's!^#(UpdateLogFile )!\1!g;' etc/freshclam.conf


## ------------------------------------------------------------

%build
CFLAGS="$RPM_OPT_FLAGS -Wall -W -Wmissing-prototypes -Wmissing-declarations -std=gnu99"
export LDFLAGS='-Wl,--as-needed'
# HACK: remove me, when configure uses $LIBS instead of $LDFLAGS for milter check
export LIBS='-lmilter -lpthread'
%configure --disable-clamav --with-dbdir=/var/lib/clamav	\
	--enable-milter --disable-static			\
	--disable-rpath						\
	%{!?with_unrar:--disable-unrar}

# build with --as-needed and disable rpath
sed -i \
	-e 's! -shared ! -Wl,--as-needed\0!g' 					\
	-e '/sys_lib_dlsearch_path_spec=\"\/lib \/usr\/lib /s!\"\/lib \/usr\/lib !/\"/%_lib /usr/%_lib !g'	\
	libtool


make %{?_smp_mflags}


## ------------------------------------------------------------

%install
rm -rf "$RPM_BUILD_ROOT" _doc*
make DESTDIR="$RPM_BUILD_ROOT" install

function smartsubst() {
	local tmp
	local regexp=$1
	shift

	tmp=$(mktemp /tmp/%name-subst.XXXXXX)
	for i; do
		sed -e "$regexp" "$i" >$tmp
		cmp -s $tmp "$i" || cat $tmp >"$i"
		rm -f $tmp
	done
}


install -d -m755 \
	${RPM_BUILD_ROOT}%_sysconfdir/{clamd.d,cron.d,logrotate.d,sysconfig} \
	${RPM_BUILD_ROOT}%_var/log \
	${RPM_BUILD_ROOT}%milterstatedir \
	${RPM_BUILD_ROOT}%pkgdatadir/template \
	${RPM_BUILD_ROOT}%_initrddir \
	${RPM_BUILD_ROOT}%homedir

rm -f	${RPM_BUILD_ROOT}%_sysconfdir/clamd.conf \
	${RPM_BUILD_ROOT}%_libdir/*.la


touch ${RPM_BUILD_ROOT}%homedir/daily.cld
touch ${RPM_BUILD_ROOT}%homedir/main.cld


## prepare the server-files
mkdir _doc_server
install -m644 -p %SOURCE2	_doc_server/clamd.sysconfig
install -m644 -p %SOURCE3       _doc_server/clamd.logrotate
install -m755 -p %SOURCE7	_doc_server/clamd.init
install -m644 -p %SOURCE5      	_doc_server/README
install -m644 -p etc/clamd.conf _doc_server/clamd.conf

install -m644 -p %SOURCE1  	$RPM_BUILD_ROOT%pkgdatadir
install -m755 -p %SOURCE100     $RPM_BUILD_ROOT%pkgdatadir
cp -pa _doc_server/*            $RPM_BUILD_ROOT%pkgdatadir/template
ln -s %pkgdatadir/clamd-wrapper $RPM_BUILD_ROOT%_initrddir/clamd-wrapper

smartsubst 's!/usr/share/clamav!%pkgdatadir!g' $RPM_BUILD_ROOT%pkgdatadir/clamd-wrapper


## prepare the update-files
install -m644 -p %SOURCE6	${RPM_BUILD_ROOT}%_sysconfdir/logrotate.d/clamav-update
install -m755 -p %SOURCE8	${RPM_BUILD_ROOT}%_sbindir/clamav-notify-servers
touch ${RPM_BUILD_ROOT}%freshclamlog

install -p -m0755 %SOURCE200	$RPM_BUILD_ROOT%pkgdatadir/freshclam-sleep
install -p -m0644 %SOURCE201	$RPM_BUILD_ROOT%_sysconfdir/sysconfig/freshclam
install -p -m0600 %SOURCE202	$RPM_BUILD_ROOT%_sysconfdir/cron.d/clamav-update

smartsubst 's!webmaster,clamav!webmaster,%username!g;
	    s!/usr/share/clamav!%pkgdatadir!g;
	    s!/usr/bin!%_bindir!g;
            s!/usr/sbin!%_sbindir!g;' \
   $RPM_BUILD_ROOT%_sysconfdir/cron.d/clamav-update \
   $RPM_BUILD_ROOT%pkgdatadir/freshclam-sleep


#### The milter stuff
function subst() {
	sed -e 's!<SERVICE>!milter!g;s!<USER>!%milteruser!g;'"$3" "$1" >"$RPM_BUILD_ROOT$2"
}


subst etc/clamd.conf /etc/clamd.d/milter.conf \
	's!^##*\(\(LogFile\|LocalSocket\|PidFile\|User\)\s\|\(StreamSaveToDisk\|ScanMail\)$\)!\1!;'


cat <<EOF >$RPM_BUILD_ROOT%_sysconfdir/sysconfig/clamav-milter
CLAMAV_FLAGS='-lo -c /etc/clamd.d/milter.conf local:%milterstatedir/clamav.sock'
EOF

install -p -m755 contrib/init/RedHat/clamav-milter $RPM_BUILD_ROOT%_initrddir/clamav-milter
touch $RPM_BUILD_ROOT%milterstatedir/clamav.sock $RPM_BUILD_ROOT%milterlog


## ------------------------------------------------------------

%clean
rm -rf "$RPM_BUILD_ROOT"

## ------------------------------------------------------------

%pre filesystem
%__fe_groupadd 4 -r %username &>/dev/null || :
%__fe_useradd  4 -r -s /sbin/nologin -d %homedir -M          \
                 -c 'Clamav database update user' -g %username %username &>/dev/null || :

%postun filesystem
%__fe_userdel  %username &>/dev/null || :
%__fe_groupdel %username &>/dev/null || :


%post update
test -e %freshclamlog || {
	touch %freshclamlog
	%__chmod 0664 %freshclamlog
	%__chown root:%username %freshclamlog
}

%pre milter-core
%__fe_groupadd 5 -r %milteruser &>/dev/null || :
%__fe_useradd  5 -r -s /sbin/nologin -d %milterstatedir -M \
                 -c 'Clamav Milter User' -g %milteruser %milteruser &>/dev/null || :

%post milter-core
test -e %milterlog || {
	touch %milterlog
	chmod 0620             %milterlog
	chown root:%milteruser %milterlog
}

%postun milter-core
%__fe_userdel  %milteruser &>/dev/null || :
%__fe_groupdel %milteruser &>/dev/null || :


%post milter-sysv
/sbin/chkconfig --add clamav-milter

%preun milter-sysv
test "$1" != 0 || %_initrddir/clamav-milter stop &>/dev/null || :
test "$1" != 0 || /sbin/chkconfig --del clamav-milter

%postun milter-sysv
test "$1"  = 0 || %_initrddir/clamav-milter condrestart >/dev/null || :


%post   lib -p /sbin/ldconfig
%postun lib -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc AUTHORS BUGS COPYING ChangeLog FAQ NEWS README UPGRADE
%doc docs/*.pdf
%_bindir/*
%_mandir/man[15]/*
%exclude %_bindir/clamav-config
%exclude %_bindir/freshclam
%exclude %_mandir/*/freshclam*

## -----------------------

%files lib
%defattr(-,root,root,-)
%_libdir/*.so.*

## -----------------------

%files devel
%defattr(-,root,root,-)
%_includedir/*
%_libdir/*.so
%pkgdatadir/template
%pkgdatadir/clamd-gen
%_libdir/pkgconfig/*
%_bindir/clamav-config

## -----------------------

%files filesystem
%attr(-,%username,%username) %dir %homedir
%attr(-,root,root)           %dir %pkgdatadir

## -----------------------

%files data
%defattr(-,%username,%username,-)
# use %%config to keep files which were updated by 'freshclam'
# already. Without this tag, they would be overridden with older
# versions whenever a new -data package is installed.
%config %verify(not size md5 mtime) %homedir/*.cvd


%files data-empty
%defattr(-,%username,%username,-)
%ghost %attr(0664,%username,%username) %homedir/*.cvd


## -----------------------

%files update
%defattr(-,root,root,-)
%_bindir/freshclam
%_mandir/*/freshclam*
%pkgdatadir/freshclam-sleep
%config(noreplace) %verify(not mtime)    %_sysconfdir/freshclam.conf
%config(noreplace) %verify(not mtime)    %_sysconfdir/logrotate.d/*
%config(noreplace) %_sysconfdir/cron.d/*
%config(noreplace) %_sysconfdir/sysconfig/freshclam

%ghost %attr(0664,root,%username) %verify(not size md5 mtime) %freshclamlog
%ghost %attr(0664,%username,%username) %homedir/*.cld


## -----------------------

%files server
%defattr(-,root,root,-)
%doc _doc_server/*
%_mandir/man[58]/clamd*
%_sbindir/*
%pkgdatadir/clamd-wrapper
%dir %_sysconfdir/clamd.d

%exclude %_sbindir/*milter*
%exclude %_mandir/man8/clamav-milter*


%files server-sysv
%defattr(-,root,root,-)
%_initrddir/clamd-wrapper


## -----------------------

%files milter
%defattr(-,root,root,-)

%files milter-core
%defattr(-,root,root,-)
%doc clamav-milter/INSTALL
%_sbindir/*milter*
%_mandir/man8/clamav-milter*
%config(noreplace) %verify(not mtime) %_sysconfdir/clamd.d/milter.conf
%ghost %attr(0620,root,%milteruser) %verify(not size md5 mtime) %milterlog

%files milter-sendmail
%defattr(-,root,root,-)
%doc clamav-milter/README.fedora
%attr(0700,%milteruser,%milteruser) %dir %milterstatedir
%ghost %milterstatedir/*

%files milter-sysv
%defattr(-,root,root,-)
%config %_initrddir/clamav-milter
%config(noreplace) %verify(not mtime) %_sysconfdir/sysconfig/clamav-milter


%changelog
* Sun Oct 26 2008 Robert Scheck <robert@fedoraproject.org> - 0.94-1
- Upgrade to 0.94 (SECURITY), fixes #461461:
- CVE-2008-1389 Invalid memory access in the CHM unpacker
- CVE-2008-3912 Out-of-memory NULL pointer dereference in mbox/msg
- CVE-2008-3913 Memory leak in code path in freshclam's manager.c
- CVE-2008-3914 Multiple file descriptor leaks on the code paths

* Sun Jul 13 2008 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.93.3-1
- updated to 0.93.3; another fix for CVE-2008-2713 (out-of-bounds read
  on petite files)
- put pid instead of pgrp into pidfile of clamav-milter (bz #452359)
- rediffed patches

* Tue Jun 17 2008 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.93.1-1
- updated to 0.93.1
- rediffed -path patch
- CVE-2008-2713 Invalid Memory Access Denial Of Service Vulnerability

* Mon Apr 14 2008 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.93-1
- updated to final 0.93
- removed daily.inc + main.inc directories; they are now replaced by
  *.cld containers
- trimmed down MAILTO list of cronjob to 'root' again; every well
  configured system has an alias for this recipient

* Wed Mar 12 2008 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.93-0.1.rc1
- moved -milter scriptlets into -milter-core subpackage
- added a requirement on the milteruser to the -milter-sendmail
  subpackage (reported by Bruce Jerrick)

* Tue Mar  4 2008 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.93-0.0.rc1
- updated to 0.93rc1
- fixed rpath issues

* Mon Feb 11 2008 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.92.1-1
- updated to 0.92.1

* Tue Jan  1 2008 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.92-6
- redisabled unrar stuff completely by using clean sources
- splitted -milter subpackage into pieces to allow use without sendmail
  (#239037)

* Tue Jan  1 2008 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.92-5
- use a better way to disable RPATH-generation (needed for '--with
  unrar' builds)

* Mon Dec 31 2007 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.92-4
- added a README.fedora to the milter package (#240610)
- ship original sources again; unrar is now licensed correctly (no more
  stolen code put under GPL). Nevertheless, this license is not GPL
  compatible, and to allow libclamav to be used by GPL applications,
  unrar is disabled by a ./configure switch.
- use pkg-config in clamav-config to emulate --cflags and --libs
  operations (fixes partly multilib issues)
- registered some more auto-updated files and marked them as %%ghost

* Fri Dec 21 2007 Tom "spot" Callaway <tcallawa@redhat.com> - 0.92-3
- updated to 0.92 (SECURITY):
- CVE-2007-6335 MEW PE File Integer Overflow Vulnerability

* Mon Oct 29 2007 Tom "spot" Callaway <tcallawa@redhat.com> - 0.91.2-3
- remove RAR decompression code from source tarball because of 
  legal problems (resolves 334371)
- correct license tag

* Mon Sep 24 2007 Jesse Keating <jkeating@redhat.com> - 0.91.2-2
- Bump release for upgrade path.

* Sat Aug 25 2007 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.91.2-1
- updated to 0.91.2 (SECURITY):
- CVE-2007-4510 DOS in RTF parser
- DOS in html normalizer
- arbitrary command execution by special crafted recipients in
  clamav-milter's black-hole mode
- fixed an open(2) issue

* Tue Jul 17 2007 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.91.1-0
- updated to 0.91.1

* Thu Jul 12 2007 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.91-1
- updated to 0.91

* Thu May 31 2007 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.90.3-1
- updated to 0.90.3
- BR tcpd.h instead of tcp_wrappers(-devel) to make it build both
  in FC6- and F7+

* Fri Apr 13 2007 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.90.2-1
- [SECURITY] updated to 0.90.2; fixes CVE-2007-1745, CVE-2007-1997 

* Fri Mar  2 2007 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.90.1-2
- BR 'tcp_wrappers-devel' instead of plain 'tcp_wrappers'

* Fri Mar  2 2007 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.90.1-1
- updated to 0.90.1
- updated %%doc list

* Sun Feb 18 2007 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.90-1
- updated to final 0.90
- removed -visibility patch since fixed upstream

* Sun Feb  4 2007 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.90-0.3.rc3
- build with -Wl,-as-needed and cleaned up pkgconfig file
- removed old hack which forced installation of freshclam.conf; related
  check was removed upstream
- removed static library
- removed %%changelog entries from before 2004

* Sat Feb  3 2007 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.90-0.2.rc3
- updated to 0.90rc3
- splitted mandatory parts from the data-file into a separate -filesystem
  subpackage
- added a -data-empty subpackage to allow a setup where database is
  updated per cron-job and user does not want to download the large
  -data package with outdated virus definitations (#214949)
- %%ghost'ed the files downloaded by freshclam

* Tue Dec 12 2006 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.88.7-1
- updated to 0.88.7

* Sun Nov  5 2006 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.88.6-1
- updated to 0.88.6

* Wed Oct 18 2006 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.88.5-1
- updated to 0.88.5 (SECURITY); fixes CVE-2006-4182, CVE-2006-5295
- added patch to set '__attribute__ ((visibility("hidden")))' for
  exported MD5_*() functions (fixes #202043)

* Thu Oct 05 2006 Christian Iseli <Christian.Iseli@licr.org> 0.88.4-4
 - rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Thu Sep 21 2006 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.88.4-3
- splitted SysV initscripts of -milter and -server into own subpackages

* Fri Sep 15 2006 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.88.4-2
- rebuilt

* Tue Aug  8 2006 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.88.4-1
- updated to 0.88.4 (SECURITY)

* Wed Jul 12 2006 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de>
- removed the clamdscan(1) manpage from the -server subpackage

* Sat Jul  8 2006 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de>
- removed a superfluous '}'
- removed some code which was relevant for FC-3 only

* Sat Jul  8 2006 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.88.3-1
- updated to 0.88.3
- updated to new fedora-usermgmt macros

* Tue May 16 2006 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.88.2-2
- cleanups: removed unneeded curlies, use plain command instead of
  %%__XXX macro, whitespace cleanup, removed unneeded versioned
  dependencies
- added a 'Requires(post): group(clamav)' dependencies for -update and
  added the corresponding Provides: to -data
- removed the %%_without_milter conditional; you won't gain anything
  when milter would be disabled at buildtime

* Sun Apr 30 2006 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.88.2-1
- updated to 0.88.2 (SECURITY)
- rediffed patches; most issues handled by 0.88.1-2 are fixed in
  0.88.2

* Mon Apr 24 2006 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.88.1-2
- added patch which fixes some classes of compiler warnings; at least
  the using of implicitly declared functions was reported to cause
  segfaults on AMD64 (brought to my attention by Marc Perkel)
- added patch which fixes wrong usage of strncpy(3) in unrarlib.c

* Thu Apr 06 2006 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.88.1-1
- updated to 0.88.1 (SECURITY)

* Sat Feb 18 2006 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.88-2
- rebuilt for FC5

* Tue Jan 10 2006 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.88-1
- updated to 0.88
- added pseudo-versions for the 'init(...)' provides as a first step
  for the support of alternative initmethods

* Tue Nov 15 2005 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.87.1-2
- moved 'freshclam.conf.5' man page into the -update subpackage (#173221)
- ship 'clamd.conf.5' man page in the -server subpackage *too*. The
  same file is contained in multiple packages now, but this man-page
  can not be removed from the base package because it also applies to
  'clamdscan' there (#173221).

* Fri Nov  4 2005 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.87.1-1
- updated to 0.87.1

* Sat Sep 17 2005 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.87-1
- updated to 0.87 (SECURITY)
- removed -timeout patch; it is solved upstream
- reverted the -exim changes; they add yet more complexity, their
  functionality can go into an own package and they contained flaws

* Fri Sep  9 2005 David Woodhouse <dwmw2@infradead.org> - 0.86.2-5
- Add clamav-exim configuration package

* Fri Jul 29 2005 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.86.2-4
- [milter] create the milter-logfile in the %%post scriptlet
- [milter] reverted the change of the default child_timeout value; it
  was set to 5 minutes in 0.86.2 which conflicts with the internal
  mode where a timeout must not be set. So, the clamav-milter would
  not run with the default configuration

* Thu Jul 28 2005 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.86.2-3
- Fixed calculation of sleep duration; on some systems/IPs, `hostid`
  results in a negative number which is retained by the bash
  modulo-operation. So the sleep may get a negative number of seconds
  being interpreted as an option. This version makes sure that the
  module-operations returns a non-negative value. [BZ #164494, James
  Wilkinson]
- added support for a /usr/sbin/clamav-notify-servers.local hook; this
  file will be executed (source'd) before all other actions and can
  abort the entire processing by invoking 'exit'

* Mon Jul 25 2005 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.86.2-2
- updated to 0.86.2 (SECURITY)
- changed the freshclam updating mechanism (again); now, it consists
  of a crontab which does not need to be changed and a helper script
  (freshclam-sleep). This helper script is configured by
  /etc/sysconfig/freshclam

* Sat Jun 25 2005 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.86.1-2
- updated to 0.86.1
- fixed randomization in %%post scriptlet: hour should be a range but
  not a single number

* Tue Jun 21 2005 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.86-1
- updated to 0.86
- randomize freshclam startup times in -update's %%post script (suggested
  by Stephen Smoogen); this requires some more Requires(post): also

* Wed May 18 2005 Warren Togami <wtogami@redhat.com> - 0.85.1-4
- fix dist tagging the way Enrico wants it

* Tue May 17 2005 Oliver Falk <oliver@linux-kernel.at>					  - 0.85.1-2
- Rebuild

* Tue May 17 2005 Oliver Falk <oliver@linux-kernel.at>					  - 0.85.1-1
- Update

* Sat May 14 2005 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.85-0
- updated to 0.85

* Sun May  1 2005 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.84-0
- updated to 0.84

* Fri Apr  7 2005 Michael Schwendt <mschwendt[AT]users.sf.net>
- rebuilt

* Tue Feb 15 2005 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.83-1
- updated to 0.83

* Tue Feb  8 2005 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.82-1
- updated to 0.82
- minor spec cleanups

* Fri Jan 28 2005 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.81-0.fdr.2
- build the package with '--disable-zlib-vcheck' because RH is unable to
  apply a fix for a 5 month old and solved security issue.  Please fill
  your comments at https://bugzilla.redhat.com/beta/show_bug.cgi?id=131385
- added 'BuildRequires: bc' (should work without also, but ./configure
  gives out ugly warnings else)

* Fri Jan 28 2005 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.81-0.fdr.1
- updated to 0.81
- do not ship the 'clamd.milter' daemon anymore; clamav-milter supports
  an internal mode now which is enabled by default
- updated -milter %%description

* Thu Jan 20 2005 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.80-0.fdr.2
- s!cron.d/clamav!cron.d/clamav-update! in the %%description of the -update
  subpackage (https://bugzilla.fedora.us/show_bug.cgi?id=1715#c39)

* Wed Nov  3 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.80-0.fdr.1
- updated to 0.80
- removed DMS, FreeBSD-HOWTO and localized docs as it is not shipped anymore
- buildrequire 'curl-devel'
- renamed clamav.conf to clamd.conf (upstream change)
- updated -initoff patch

* Tue Sep 14 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.75.1-0.fdr.1
- updated to 0.75.1
- use %%configure, the problems with the architecture specification
  seem to have passed (probably because of an autoconf update)
- set mode 0600 for the cron-script (required by vixie-cron)
- made the cronjob a spambot and send mail about deactivated freshclam
  service to nearly everybody... (root, postmaster, webmaster)
- other fixes in the notification cronjob

* Fri Jul 23 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.75-0.fdr.1
- updated to 0.75

* Thu Jul 15 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.74-0.fdr.2
- moved /usr/bin/clamav-config from main into -devel

* Wed Jun 30 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.74-0.fdr.1
- updated to 0.74

* Mon Jun 14 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.73-0.fdr.1
- updated to 0.73
- added pkgconfig file

* Fri Jun 11 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.72-0.fdr.3
- notify the user about a deactivated clamav-update service
- added clamd-gen script which generates template spec-files for
  services using clamd
- copied template configuration files to %pkgdatadir/template (needed
  for clamd-gen)
- moved the clamd-wrapper from %_initrddir to %{pkgdatadir}; a symlink
  will be provided for compatibility reasons
- conditionalized building of the -milter subpackage ('--without
  milter' switch) to enable builds on RH73 (bug #1715, comment #5/#7)

* Fri Jun  4 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.72-0.fdr.2
- removed 'BuildRequires: dietlibc'; it was a leftover from the
  pre-use-signal era (before 0.70) (bug #1716)

* Thu Jun  3 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.72-0.fdr.1
- updated to 0.72

* Thu May 20 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.71-0.fdr.2
- removed the randomization in the cronjob; it seems to be impossible
  to use the mod-operator (%%) there. Instead of, the user has to
  replace some placeholders...

* Wed May 19 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.71-0.fdr.1
- updated to 0.71

* Fri May  7 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.70-0.fdr.1.1
- quote 'EOF' to delay $RANDOM expansion

* Tue Apr 27 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.70-0.fdr.2
- updated GECOS entry for the 'clamav' user to describe its purpose
  more accurately
- use explicit '-m755' when creating directories with install

* Tue Apr 20 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.70-0.fdr.1
- updated to 0.70; rediffed some patches
- updated logrotate script to use signals and documented the steps
  which are needed to make it work
- adapted initscript to use signals instead of sockwrite
- removed sockwrite; signals can now be used to reload the database
- added logfile to the -milter subpackage

* Tue Apr 20 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.68-0.fdr.2.1
- tagged some Requires:, since clamav-server is required in the milter-%%post* scriptlets

* Sat Mar 20 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.68-0.fdr.2
- split the double Requires(...,...): statements; see
  https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=118773
- require the recent fedora-usermgmt package (0.7) which fixes similar
  ordering issues

* Thu Mar 18 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.68-0.fdr.1
- updated to 0.68 (using the -1 version)
- ship milter-files in the -milter instead of the -server subpackage

* Tue Feb 24 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.67-0.fdr.3
- fixed ':' vs. '.' in chown

* Tue Feb 17 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.67-0.fdr.2
- randomize freshclam startup to prevent server peaks

* Mon Feb 16 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.67-0.fdr.1
- updated to 0.67 (using the -1 version)

* Wed Feb 11 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.66-0.fdr.2
- updated to 0.66; important, packaging-relevant changes are
  freshclam:
  * $http_proxy is not supported anymore; you have to configure it in
    /etc/freshclam.conf
  * the logfile has been renamed to /var/log/freshclam.log
- removed %%check section; buildroot check is implemented in local
  testsuite already
- added some %%verify(not mtime) modifiers to avoid unnecessary .rpmnew
  files
- added some directory-Requires:
- activated milter-package and made it work
- added patch to disable clamav-milter service by default
- renamed /var/run/clamav.<SERVICE> to /var/run/clamd.<SERVICE>; this
  makes things more consistently but can break backward compatibility. The
  initscript should deal with the old version too, but I would not bet on
  it...
- updated some descriptions
- fixed the update-mechanism; now it happens in two stages: at first,
  the files will be downloaded as user 'clamav' and then, root initiates
  the daemon-reload.

* Mon Feb  9 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.65-0.fdr.5
- added security fix for
  http://www.securityfocus.com/archive/1/353194/2004-02-06/2004-02-12/1
