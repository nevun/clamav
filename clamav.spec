## $Id: clamav.spec,v 1.37 2006/07/08 15:57:54 ensc Exp $

## Fedora Extras specific customization below...
%bcond_without       fedora
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
Version:	0.88.4
Release:	%release_func 1

License:	GPL
Group:		Applications/File
URL:		http://www.clamav.net
Source0:	http://download.sourceforge.net/sourceforge/clamav/%name-%version.tar.gz
Source999:	http://download.sourceforge.net/sourceforge/clamav/%name-%version.tar.gz.sig
Source1:	clamd-wrapper
Source2:	clamd.sysconfig
Source3:	clamd.logrotate
Source5:	clamd-README
Source6:	clamav-update.logrotate
Source7:	clamd.SERVICE.init
Source8:	clamav-notify-servers
Patch0:		clamav-0.88.2-guys,please-read-the-compiler-warnings-before-doing-a-release.patch
Patch1:		clamav-0.88.1-strncpy.patch
Patch20:	clamav-0.70-user.patch
Patch21:	clamav-0.70-path.patch
Patch22:	clamav-0.80-initoff.patch
BuildRoot:	%_tmppath/%name-%version-%release-root
Requires:	clamav-lib = %version-%release
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
Requires:	clamav-lib = %version-%release
Requires(pre):	%_libdir/pkgconfig

%package data
Summary:	Virus signature data for the Clam Antivirus scanner
Group:		Applications/File
Provides:	data(clamav)
Provides:	user(clamav)
Provides:	group(clamav)
BuildRequires:	fedora-usermgmt-devel
%{?FE_USERADD_REQ}

%package update
Summary:	Auto-updater for the Clam Antivirus scanner data-files
Group:		Applications/File
Source200:	freshclam-sleep
Source201:	freshclam.sysconfig
Source202:	clamav-update.cron
Requires:	clamav-data = %version-%release
Requires(pre):		/etc/cron.d
Requires(postun):	/etc/cron.d
Requires(post):		%__chown %__chmod
Requires(post):		group(clamav)

%package server
Summary:	Clam Antivirus scanner server
Group:		System Environment/Daemons
Provides:	clamav-daemon = %version-%release
Obsoletes:	clamav-daemon < %version-%release
Conflicts:	clamav-daemon > %version-%release
## For now, use this as a placeholder. Later, generate separate -sysv
## and -minit subpackages
Requires:	init(clamav-server)
Provides:	init(clamav-server) = sysv
Requires:	data(clamav)
Requires:	clamav-lib = %version-%release
Requires(pre):		%_initrddir
Requires(postun):	%_initrddir

%package milter
Summary:	Sendmail-milter for the Clam Antivirus scanner
Group:		System Environment/Daemons
## For now, use this as a placeholder. Later, generate separate -sysv
## and -minit subpackages
Requires:	init(clamav-milter)
Provides:	init(clamav-milter) = sysv
BuildRequires:	sendmail-devel
BuildRequires:	fedora-usermgmt-devel
Requires:		sendmail
Requires(pre):		%_initrddir
Requires(postun):	%_initrddir initscripts
Requires(post):		chkconfig coreutils
Requires(preun):	chkconfig initscripts
%{?FE_USERADD_REQ}


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
%patch0  -p1 -b '.guys,please-read-the-compiler-warnings-before-doing-a-release.patch'
%patch1  -p1 -b .strncpy

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
CFLAGS="$RPM_OPT_FLAGS -Wall -W -Wmissing-prototypes -Wmissing-declarations -std=gnu99"
%configure --disable-clamav --with-dbdir=/var/lib/clamav \
	   --enable-milter

## HACK: ./configure checks if freshclam.conf/clamd.conf are existing
## in current filesystem and skips its installation then. Was introduced
## by 0.66.
perl -pi -e 's!^(s,\@INSTALL_(CLAMAV|FRESHCLAM)_CONF_TRUE\@),[^,]*,!\1,,!g;
             s!^(s,\@INSTALL_(CLAMAV|FRESHCLAM)_CONF_FALSE\@),[^,]*,!\1,\#,!g' config.status
./config.status

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
	${RPM_BUILD_ROOT}%_initrddir

rm -f	${RPM_BUILD_ROOT}%_sysconfdir/clamd.conf \
	${RPM_BUILD_ROOT}%_libdir/*.la


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
## The '-blo' options might be usefully here -- especially for testing; see
## "man 8 clamav-milter" for further options
CLAMAV_FLAGS='--max-children=2 -c /etc/clamd.d/milter.conf local:%milterstatedir/clamav.sock'
CLAMAV_USER='%milteruser'
EOF

install -p -m755 contrib/init/RedHat/clamav-milter $RPM_BUILD_ROOT%_initrddir/clamav-milter
touch $RPM_BUILD_ROOT%milterstatedir/clamav.sock $RPM_BUILD_ROOT%milterlog


## ------------------------------------------------------------

%clean
rm -rf "$RPM_BUILD_ROOT"

## ------------------------------------------------------------

%pre data
%__fe_groupadd 4 -r %username &>/dev/null || :
%__fe_useradd  4 -r -s /sbin/nologin -d %homedir -M          \
                 -c 'Clamav database update user' -g %username %username &>/dev/null || :

%post update
test -e %freshclamlog || {
	touch %freshclamlog
	%__chmod 0664 %freshclamlog
	%__chown root:%username %freshclamlog
}

%postun data
%__fe_userdel  %username &>/dev/null || :
%__fe_groupdel %username &>/dev/null || :

%pre milter
%__fe_groupadd 5 -r %milteruser &>/dev/null || :
%__fe_useradd  5 -r -s /sbin/nologin -d %milterstatedir -M \
                 -c 'Clamav Milter User' -g %milteruser %milteruser &>/dev/null || :

%post milter
/sbin/chkconfig --add clamav-milter
test -e %milterlog || {
	touch %milterlog
	chmod 0620             %milterlog
	chown root:%milteruser %milterlog
}

%preun milter
test "$1" != 0 || %_initrddir/clamav-milter stop &>/dev/null || :
test "$1" != 0 || /sbin/chkconfig --del clamav-milter

%postun milter
%__fe_userdel  %milteruser &>/dev/null || :
%__fe_groupdel %milteruser &>/dev/null || :
test "$1"  = 0 || %_initrddir/clamav-milter condrestart >/dev/null || :


%post   lib -p /sbin/ldconfig
%postun lib -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc AUTHORS BUGS COPYING ChangeLog FAQ NEWS TODO
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
%_libdir/*.*a
%_libdir/*.so
%dir %pkgdatadir
%pkgdatadir/template
%pkgdatadir/clamd-gen
%_libdir/pkgconfig/*
%_bindir/clamav-config

## -----------------------

%files data
%defattr(-,%username,%username,-)
%dir %homedir
# use %%config to keep files which were updated by 'freshclam'
# already. Without this tag, they would be overridden with older
# versions whenever a new -data package is installed.
%config %verify(not size md5 mtime) %homedir/*.cvd

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

## -----------------------

%files server
%defattr(-,root,root,-)
%doc _doc_server/*
%doc %_mandir/man[58]/clamd*
%_sbindir/*
%_initrddir/clamd-wrapper
%dir %pkgdatadir
%dir %_sysconfdir/clamd.d
%pkgdatadir/clamd-wrapper


%exclude %_sbindir/*milter*
%exclude %_mandir/man8/clamav-milter*

## -----------------------

%files milter
%defattr(-,root,root,-)
%doc clamav-milter/INSTALL
%_sbindir/*milter*
%_mandir/man8/clamav-milter*
%config %_initrddir/clamav-milter
%config(noreplace) %verify(not mtime) %_sysconfdir/clamd.d/milter.conf
%config(noreplace) %verify(not mtime) %_sysconfdir/sysconfig/clamav-milter
%attr(0700,%milteruser,%milteruser) %dir %milterstatedir
%ghost %milterstatedir/*
%ghost %attr(0620,root,%milteruser) %verify(not size md5 mtime) %milterlog

%changelog
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
