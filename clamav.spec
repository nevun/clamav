## $Id: clamav.spec,v 1.22 2005/06/25 17:38:35 ensc Exp $

## This package understands the following switches:
## --without milter          ...  deactivate the -milter subpackage


## Fedora Extras specific customization below...
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
Version:	0.86.1
Release:	%release_func 2

License:	GPL
Group:		Applications/File
URL:		http://www.clamav.net
Source0:	http://download.sourceforge.net/sourceforge/clamav/%{name}-%{version}.tar.gz
#Source999:	http://download.sourceforge.net/sourceforge/clamav/%{name}-%{version}.tar.gz.sig
Source1:	clamd-wrapper
Source2:	clamd.sysconfig
Source3:	clamd.logrotate
Source5:	clamd-README
Source6:	clamav-update.logrotate
Source7:	clamd.SERVICE.init
Source8:	clamav-notify-servers
Patch20:	clamav-0.70-user.patch
Patch21:	clamav-0.70-path.patch
Patch22:	clamav-0.80-initoff.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root
Requires:	clamav-lib = %{version}-%{release}
Requires:	data(clamav)
BuildRequires:	zlib-devel bzip2-devel gmp-devel tcp_wrappers curl-devel
BuildRequires:	bc

%package lib
Summary:	Dynamic libraries for the Clam Antivirus scanner
Group:		System Environment/Libraries
Requires:	data(clamav)

%package devel
Summary:	Header files and libraries for the Clam Antivirus scanner
Group:		Development/Libraries
Source100:	clamd-gen
Requires:	clamav-lib = %{version}-%{release}
Requires(pre):	%_libdir/pkgconfig

%package data
Summary:	Virus signature data for the Clam Antivirus scanner
Group:		Applications/File
Provides:	data(clamav)
Requires(pre):		fedora-usermgmt >= 0.7
Requires(postun):	fedora-usermgmt >= 0.7

%package update
Summary:	Auto-updater for the Clam Antivirus scanner data-files
Group:		Applications/File
Requires:	clamav-data = %{version}-%{release}
Requires(pre):		/etc/cron.d
Requires(postun):	/etc/cron.d
Requires(post):		%__chown %__chmod %__sed diffutils

%package server
Summary:	Clam Antivirus scanner server
Group:		System Environment/Daemons
Provides:	clamav-daemon = %{version}-%{release}
Obsoletes:	clamav-daemon < %{version}-%{release}
Conflicts:	clamav-daemon > %{version}-%{release}
## For now, use this as a placeholder. Later, generate separate -sysv
## and -minit subpackages
Requires:	init(clamav-server)
Provides:	init(clamav-server)
Requires:	data(clamav)
Requires:	clamav-lib = %{version}-%{release}
Requires(pre):		%_initrddir
Requires(postun):	%_initrddir

%package milter
Summary:	Sendmail-milter for the Clam Antivirus scanner
Group:		System Environment/Daemons
## For now, use this as a placeholder. Later, generate separate -sysv
## and -minit subpackages
Requires:	init(clamav-milter)
Provides:	init(clamav-milter)
%{!?_without_milter:BuildRequires:	sendmail-devel}
Requires:		sendmail
Requires(pre):		%_initrddir
Requires(postun):	%_initrddir
Requires(post):		chkconfig
Requires(preun):	chkconfig
Requires(preun):	initscripts
Requires(postun):	initscripts
Requires(pre):		fedora-usermgmt >= 0.7
Requires(postun):	fedora-usermgmt >= 0.7


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


%description lib
This package contains dynamic libraries shared between applications
using the Clam Antivirus scanner.

%description devel
This package contains headerfiles and libraries which are needed to
build applications using clamav.

%description data
This package contains the virus-database needed by clamav. This
database should be updated regularly; the 'clamav-update' package
ships a corresponding cron-job.

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

%description milter
This package contains files which are needed to run the clamav-milter. It
can be activated by adding

| INPUT_MAIL_FILTER(`clamav', `S=local:%milterstatedir/clamav.sock, F=, T=S:4m;R:4m')dnl

to your sendmail.mc.

THIS PACKAGE IS TO BE CONSIDERED AS EXPERIMENTAL!

## ------------------------------------------------------------

%prep
%setup -q
%patch20 -p1 -b .user
%patch21 -p1 -b .path
%patch22 -p1 -b .initoff

perl -pi -e 's!^(#?LogFile ).*!\1/var/log/clamd.<SERVICE>!g;
	     s!^#?(LocalSocket ).*!\1/var/run/clamd.<SERVICE>/clamd.sock!g;
	     s!^#?(PidFile ).*!\1/var/run/clamd.<SERVICE>/clamd.pid!g;
	     s!^#?(User ).*!\1<USER>!g;
             s! /usr/local/share/clamav,! %homedir,!g;
            ' etc/clamd.conf

perl -pi -e 's!^#(UpdateLogFile )!\1!g;' etc/freshclam.conf

## ------------------------------------------------------------

%build
## '--disable-zlib-vcheck' is used because every FC<=3 ships zlib-1.2.1*
## but clamav checks for zlib >= 1.2.2.  This option can be removed for
## FC4 builds.
##
## See https://bugzilla.redhat.com/beta/show_bug.cgi?id=131385 and
## http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=CAN-2004-0797
## also
%configure --disable-clamav --with-dbdir=/var/lib/clamav \
           --disable-zlib-vcheck \
	   %{!?_without_milter:--enable-milter}

## HACK: ./configure checks if freshclam.conf/clamd.conf are existing
## in current filesystem and skips its installation then. Was introduced
## by 0.66.
perl -pi -e 's!^(s,\@INSTALL_(CLAMAV|FRESHCLAM)_CONF_TRUE\@),[^,]*,!\1,,!g;
             s!^(s,\@INSTALL_(CLAMAV|FRESHCLAM)_CONF_FALSE\@),[^,]*,!\1,\#,!g' config.status
./config.status

%{__make} %{?_smp_mflags}


## ------------------------------------------------------------

%install
rm -rf "$RPM_BUILD_ROOT" _doc*
%{__make} DESTDIR="$RPM_BUILD_ROOT" install

%{__install} -d -m755 \
	${RPM_BUILD_ROOT}%{_sysconfdir}/{clamd.d,cron.d,logrotate.d,sysconfig} \
	${RPM_BUILD_ROOT}%{_var}/log \
	${RPM_BUILD_ROOT}%milterstatedir \
	${RPM_BUILD_ROOT}%pkgdatadir/template \
	${RPM_BUILD_ROOT}%{_initrddir}

rm -f	${RPM_BUILD_ROOT}%{_sysconfdir}/clamd.conf \
	${RPM_BUILD_ROOT}%{_libdir}/*.la

%{?_without_milter:rm -f $RPM_BUILD_ROOT%_mandir/*/*milter*}


## prepare the server-files
mkdir _doc_server
%{__install} -m644 -p %{SOURCE2}	_doc_server/clamd.sysconfig
%{__install} -m644 -p %{SOURCE3}       	_doc_server/clamd.logrotate
%{__install} -m755 -p %{SOURCE7}	_doc_server/clamd.init
%{__install} -m644 -p %{SOURCE5}       	_doc_server/README
%__install   -m644 -p etc/clamd.conf    _doc_server/clamd.conf

%__install   -m644 -p %SOURCE1  	$RPM_BUILD_ROOT%pkgdatadir
%__install   -m755 -p %SOURCE100        $RPM_BUILD_ROOT%pkgdatadir
cp -pa _doc_server/*                    $RPM_BUILD_ROOT%pkgdatadir/template
ln -s %pkgdatadir/clamd-wrapper         $RPM_BUILD_ROOT%_initrddir/clamd-wrapper

f=$RPM_BUILD_ROOT%pkgdatadir/clamd-wrapper
sed -e 's!/usr/share/clamav!%pkgdatadir!g' "$f" >"$f".tmp
cmp -s "$f" "$f".tmp || cat "$f".tmp >"$f"
rm -f "$f".tmp


## prepare the update-files
%{__install} -m644 -p %{SOURCE6}	${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d/clamav-update
%{__install} -m755 -p %{SOURCE8}	${RPM_BUILD_ROOT}%{_sbindir}/clamav-notify-servers
touch ${RPM_BUILD_ROOT}%{freshclamlog}

cat >${RPM_BUILD_ROOT}%{_sysconfdir}/cron.d/clamav-update <<"EOF"
## Adjust this line...
MAILTO=root,postmaster,webmaster,%username

## It is ok to execute it as root; freshclam drops privileges and becomes
## user 'clamav' as soon as possible
# @MIN@  @HOUR@/3 * * * root %{_bindir}/freshclam --quiet && { test -x %{_sbindir}/clamav-notify-servers && exec %{_sbindir}/clamav-notify-servers || :; }

## Comment out or remove this line...
1 8 * * * %username /bin/sh -c 'echo "Please activate the clamav update in %_sysconfdir/cron.d/clamav-update" >&2'
EOF

%if 0%{!?_without_milter:1}
#### The milter stuff

function subst() {
	sed -e 's!<SERVICE>!milter!g;s!<USER>!%milteruser!g;'"$3" "$1" >"$RPM_BUILD_ROOT$2"
}

subst etc/clamd.conf /etc/clamd.d/milter.conf \
	's!^##*\(\(LogFile\|LocalSocket\|PidFile\|User\)\s\|\(StreamSaveToDisk\|ScanMail\)$\)!\1!;'


cat <<EOF >$RPM_BUILD_ROOT%_sysconfdir/sysconfig/clamav-milter
## The '-blo' options might be usefully here -- especially for testing; see
## "man 8 clamav-milter" for further options
CLAMAV_FLAGS='--max-children=2 -c /etc/clamd.d/milter.conf local:%milterstatedir/clamav.sock'
CLAMAV_USER='%milteruser'
EOF

%__install -p -m755 contrib/init/RedHat/clamav-milter $RPM_BUILD_ROOT%_initrddir/clamav-milter
touch $RPM_BUILD_ROOT%milterstatedir/clamav.sock $RPM_BUILD_ROOT%milterlog
%endif	# _without_milter


## ------------------------------------------------------------

%clean
rm -rf "$RPM_BUILD_ROOT"

## ------------------------------------------------------------

%pre data
/usr/sbin/fedora-groupadd 4 -r %{username} &>/dev/null || :
/usr/sbin/fedora-useradd  4 -r -s /sbin/nologin -d %{homedir} -M          \
                            -c 'Clamav database update user' -g %{username} %{username} &>/dev/null || :

%post update
test -e %{freshclamlog} || {
	touch %{freshclamlog}
	%{__chmod} 0664 %{freshclamlog}
	%{__chown} root:%{username} %{freshclamlog}
}

min=$[ RANDOM % 60 ]
hour=$[ RANDOM % 3 ]
tmp=$(mktemp /tmp/freshclam-cron.XXXXXX)
src=%_sysconfdir/cron.d/clamav-update
%__sed -e "s!@MIN@!$min!g;s!@HOUR@!$hour-23!g" "$src" >$tmp
cmp -s $tmp "$src" || cat "$tmp" >"$src"
rm -f $tmp


%postun data
test "$1" != 0 || /usr/sbin/fedora-userdel  %{username} &>/dev/null || :
test "$1" != 0 || /usr/sbin/fedora-groupdel %{username} &>/dev/null || :

%pre milter
/usr/sbin/fedora-groupadd 5 -r %milteruser &>/dev/null || :
/usr/sbin/fedora-useradd  5 -r -s /sbin/nologin -d %milterstatedir -M \
                            -c 'Clamav Milter User' -g %milteruser %milteruser &>/dev/null || :

%post milter
/sbin/chkconfig --add clamav-milter

%preun milter
test "$1" != 0 || %{_initrddir}/clamav-milter stop &>/dev/null || :
test "$1" != 0 || /sbin/chkconfig --del clamav-milter

%postun milter
test "$1" != 0 || /usr/sbin/fedora-userdel  %{milteruser} &>/dev/null || :
test "$1" != 0 || /usr/sbin/fedora-groupdel %{milteruser} &>/dev/null || :
test "$1"  = 0 || %{_initrddir}/clamav-milter condrestart >/dev/null || :


%post   lib -p /sbin/ldconfig
%postun lib -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc AUTHORS BUGS COPYING ChangeLog FAQ NEWS TODO
%doc docs/*.pdf
%doc %{_mandir}/man[15]/*
%{_bindir}/*
%exclude %_bindir/clamav-config
%exclude %_bindir/freshclam
%exclude %_mandir/man1/freshclam*

## -----------------------

%files lib
%defattr(-,root,root,-)
%{_libdir}/*.so.*

## -----------------------

%files devel
%defattr(-,root,root,-)
%{_includedir}/*
%{_libdir}/*.*a
%{_libdir}/*.so
%dir %pkgdatadir
%pkgdatadir/template
%pkgdatadir/clamd-gen
%_libdir/pkgconfig/*
%_bindir/clamav-config

## -----------------------

%files data
%defattr(-,%{username},%{username},-)
%dir %{homedir}
# use %%config to keep files which were updated by 'freshclam'
# already. Without this tag, they would be overridden with older
# versions whenever a new -data package is installed.
%config %verify(not size md5 mtime) %{homedir}/*.cvd

## -----------------------

%files update
%defattr(-,root,root,-)
%_bindir/freshclam
%_mandir/man1/freshclam*
%config(noreplace) %verify(not mtime) %_sysconfdir/freshclam.conf
%config(noreplace) %verify(not mtime) %attr(0600,root,root) %_sysconfdir/cron.d/*
%config(noreplace) %verify(not mtime) %_sysconfdir/logrotate.d/*

%ghost %attr(0664,root,%{username}) %verify(not size md5 mtime) %{freshclamlog}

## -----------------------

%files server
%defattr(-,root,root,-)
%doc _doc_server/*
%doc %{_mandir}/man8/*
%{_sbindir}/*
%_initrddir/clamd-wrapper
%dir %pkgdatadir
%dir %{_sysconfdir}/clamd.d
%pkgdatadir/clamd-wrapper


%if 0%{!?_without_milter:1}
%exclude %_sbindir/*milter*
%exclude %_mandir/man8/clamav-milter*

## -----------------------

%files milter
%defattr(-,root,root,-)
%doc clamav-milter/INSTALL
%_sbindir/*milter*
%_mandir/man8/clamav-milter*
%config %{_initrddir}/clamav-milter
%config(noreplace) %verify(not mtime) %{_sysconfdir}/clamd.d/milter.conf
%config(noreplace) %verify(not mtime) %{_sysconfdir}/sysconfig/clamav-milter
%attr(0700,%milteruser,%milteruser) %dir %milterstatedir
%ghost %milterstatedir/*
%ghost %attr(0620,root,%milteruser) %verify(not size md5 mtime) %milterlog
%endif	# _without_milter

%changelog
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

* Fri Nov 28 2003 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.65-0.fdr.4
- fixed typo in README (sysconf.d vs. sysconf)
- make build on rhl8 succeed by adding '|| :' to %%check

* Tue Nov 18 2003 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.65-0.fdr.3
- substitute 'User' in sample cfg-file also
- uncommented some cfg-options which are needed for a proper operation
- fixed typos in README (thanks to Michael Schwendt)

* Mon Nov 17 2003 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.65-0.fdr.2
- fixed path of 'LocalSocket' and documented steps how to create it
- added a missing backslash at the configure-call
- do not package clamav-milter.8 manpage
- documented 'User' in the README

* Sat Nov 15 2003 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.65-0.fdr.1
- updated to 0.65
- added gmp-devel buildrequires:
- changed installed databases from 'viruses.db*' to '*.cvb'
- made milter-build conditional; 0.65 is missing some files which would break the build else
- fixed typo (clamav-notify-server -> clamav-notify-servers)

* Fri Oct 31 2003 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.60-0.fdr.5
- created -update subpackage and filled it with files from main and -data package
- set more reasonable default-values in the sample config-file
- made the README in -server more clear
- moved clamav-milter man-page into -milter subpackage
- use fedora-usermgmt
- renamed -daemon subpackage and related files to -server
- use abstract 'data(clamav)' notation for clamav-data dependencies
- use 'init(...)' requirements as placeholder for future -sysv/-minit subpackages

* Sat Aug 16 2003 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> 0:0.60-0.fdr.4
- backported clamav-sockwrite.c to C89

* Fri Aug 15 2003 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> 0:0.60-0.fdr.3
- updated Source0 URL
- fixed portuguese i18n-abbreviation

* Fri Jul 18 2003 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> 0:0.60-0.fdr.3
- use LSB compliant exit-codes in the init-script
- other init-script cleanups

* Tue Jul 15 2003 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> 0:0.60-0.fdr.2
- updated %%description
- removed README from %%doc-list

* Thu Jun 26 2003 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> 0:0.60-0.fdr.1
- disabled -milter subpackage; I do not get it to run :(

* Thu Jun 26 2003 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> 0:0.60-0.fdr.0.1
- updated to 0.60
- modernized usercreation
- added -milter subpackage

* Thu May  8 2003 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> 0:0.54-0.fdr.2
- added BUGS file
- moved clamd.8 man-page into daemon-subpackage
- some cosmetical cleanups
- removed config-patch; it was unused
- made some paths more fedora-compliant
- honor $RPM_OPT_FLAGS
- added clamav-notify-daemons script
- removed obsoleted %%socketdir

* Wed May  7 2003 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> 0:0.54-0.fdr.0.1
- splitted into additional -data/-daemon packages
- added clamav-sockwrite program
- updated to recent fedora policies

* Thu Nov 21 2002 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> 0.54-1
- updated to 0.54
- updated config-patch

* Tue Oct 29 2002 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> 0.52-1
- updated to 0.52

* Tue Sep 17 2002 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de>
- Initial build.
