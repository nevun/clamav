%define username	clamav
%define homedir		%_var/lib/clamav
%define freshclamlog	%_var/log/freshclam.log
%define milterlog	%_var/log/clamd.milter
%define milteruser	clamilt
%define milterstatedir	%_var/run/clamav-milter
%define milterclamddir	%_var/run/clamd.milter

Summary:	End-user tools for the Clam Antivirus scanner
Name:		clamav
Version:	0.71
Release:	0.fdr.2.2
Epoch:		0
License:	GPL
Group:		Applications/File
URL:		http://www.clamav.net
Source0:	http://download.sourceforge.net/sourceforge/clamav/%{name}-%{version}.tar.gz
Source999:	http://download.sourceforge.net/sourceforge/clamav/%{name}-%{version}.tar.gz.sig
Source1:	clamd-wrapper
Source2:	clamd.sysconfig
Source3:	clamd.logrotate
Source5:	clamd-README
Source6:	clamav-update.logrotate
Source7:	clamd.SERVICE.init
Source8:	clamav-notify-servers
Patch20:	clamav-0.70-user.patch
Patch21:	clamav-0.70-path.patch
Patch22:	clamav-0.70-initoff.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root
Requires:	clamav-lib = %{epoch}:%{version}-%{release}
Requires:	data(clamav)
BuildRequires:	zlib-devel bzip2-devel gmp-devel tcp_wrappers

%package lib
Summary:	Dynamic libraries for the Clam Antivirus scanner
Group:		System Environment/Libraries
Requires:	data(clamav)

%package devel
Summary:	Headerfiles and libraries for the Clam Antivirus scanner
Group:		Development/Libraries
Requires:	clamav-lib = %{epoch}:%{version}-%{release}

%package data
Summary:	The virus-signatures for clamav
Group:		Applications/File
Provides:	data(clamav)
Requires(pre):		fedora-usermgmt >= 0:0.7
Requires(postun):	fedora-usermgmt >= 0:0.7

%package update
Summary:	Auto-updater for clamav data-files
Group:		Applications/File
Requires:	clamav-data = %epoch:%version-%release
Requires(pre):		/etc/cron.d
Requires(postun):	/etc/cron.d
Requires(post):		%{__chown} %{__chmod}

%package server
Summary:	The clamav server
Group:		System Environment/Daemons
Provides:	clamav-daemon = %epoch:%version-%release
Obsoletes:	clamav-daemon < %epoch:%version-%release
Conflicts:	clamav-daemon > %epoch:%version-%release
## For now, use this as a placeholder. Later, generate separate -sysv
## and -minit subpackages
Requires:	init(clamav-server)
Provides:	init(clamav-server)
Requires:	data(clamav)
Requires:	clamav-lib = %{epoch}:%{version}-%{release}
BuildRequires:	dietlibc
Requires(pre):		%_initrddir
Requires(postun):	%_initrddir

%package milter
Summary:	A sendmail-milter for clamav
Group:		System Environment/Daemons
## For now, use this as a placeholder. Later, generate separate -sysv
## and -minit subpackages
Requires:	init(clamav-milter)
Provides:	init(clamav-milter)
BuildRequires:	sendmail-devel
Requires(preun):	clamav-server = %{epoch}:%{version}-%{release}
Requires(postun):	clamav-server = %{epoch}:%{version}-%{release}
Requires:		sendmail
Requires(pre):		%_initrddir
Requires(postun):	%_initrddir
Requires(post):		chkconfig
Requires(preun):	chkconfig
Requires(preun):	initscripts
Requires(postun):	initscripts
Requires(pre):		fedora-usermgmt >= 0:0.7
Requires(postun):	fedora-usermgmt >= 0:0.7


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
this task. To activate it, uncomment the entry in /etc/cron.d/clamav.

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
| define(`confINPUT_MAIL_FILTERS', `clamav')dnl

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
            ' etc/clamav.conf

perl -pi -e 's!^#(UpdateLogFile )!\1!g;' etc/freshclam.conf

## ------------------------------------------------------------

%build
#%%configure --disable-clamav --with-dbdir=/var/lib/clamav
## The %%configure macro can not be used since the script breaks on
## the old architecture specification

CFLAGS=$RPM_OPT_FLAGS; export CFLAGS
./configure --prefix=%{_prefix} --mandir=%{_mandir} --sysconfdir=%{_sysconfdir}	\
	--disable-clamav --with-dbdir=%{homedir} \
	--enable-milter

## HACK: ./configure checks if freshclam.conf/clamav.conf are existing
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
	${RPM_BUILD_ROOT}{%milterstatedir,%milterclamddir} \
	${RPM_BUILD_ROOT}%{_initrddir}

rm -f	${RPM_BUILD_ROOT}%{_sysconfdir}/clamav.conf \
	${RPM_BUILD_ROOT}%{_libdir}/*.la


## prepare the server-files
mkdir _doc_server
%{__install} -m644 -p %{SOURCE1}       	${RPM_BUILD_ROOT}%{_initrddir}/clamd-wrapper
%{__install} -m644 -p %{SOURCE2}	_doc_server/clamd.sysconfig
%{__install} -m644 -p %{SOURCE3}       	_doc_server/clamd.logrotate
%{__install} -m755 -p %{SOURCE7}	_doc_server/clamd.init
%{__install} -m644 -p %{SOURCE5}       	_doc_server/README

## prepare the update-files
%{__install} -m644 -p %{SOURCE6}	${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d/clamav-update
%{__install} -m755 -p %{SOURCE8}	${RPM_BUILD_ROOT}%{_sbindir}/clamav-notify-servers
touch ${RPM_BUILD_ROOT}%{freshclamlog}

cat >${RPM_BUILD_ROOT}%{_sysconfdir}/cron.d/clamav-update <<"EOF"
## It is ok to execute it as root; freshclam drops privileges and becomes
## user 'clamav' as soon as possible
## Note: replace 'MIN' and 'HOUR' with random values
# MIN  HOUR/3 * * * root %{_bindir}/freshclam --quiet && { test -x %{_sbindir}/clamav-notify-servers && exec %{_sbindir}/clamav-notify-servers || :; }
EOF


#### The milter stuff

function subst() {
	sed -e 's!<SERVICE>!milter!g;s!<USER>!%milteruser!g;'"$3" "$1" >"$RPM_BUILD_ROOT$2"
}

subst %SOURCE3        /etc/logrotate.d/clamd.milter
subst %SOURCE7        %_initrddir/clamd.milter
subst etc/clamav.conf /etc/clamd.d/milter.conf \
	's!^##*\(\(LogFile\|LocalSocket\|PidFile\|User\)\s\|\(StreamSaveToDisk\|ScanMail\)$\)!\1!;'

chmod 0755 $RPM_BUILD_ROOT%_initrddir/clamd.milter
ln -s ./clamd $RPM_BUILD_ROOT%_sbindir/clamd.milter

cat <<EOF >$RPM_BUILD_ROOT%_sysconfdir/sysconfig/clamav-milter
## The '-blo' options might be usefully here -- especially for testing; see
## "man 8 clamav-milter" for further options
CLAMAV_FLAGS='--max-children=2 -c /etc/clamd.d/milter.conf local:%milterstatedir/clamav.sock'
CLAMAV_USER='%milteruser'
EOF

%__install -p -m755 contrib/init/RedHat/clamav-milter $RPM_BUILD_ROOT%_initrddir/clamav-milter
touch $RPM_BUILD_ROOT%milterclamddir/{clamd.sock,clamd.pid,milter.sock}
touch $RPM_BUILD_ROOT%milterstatedir/clamav.sock $RPM_BUILD_ROOT%milterlog

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

%postun data
test "$1" != 0 || /usr/sbin/fedora-userdel  %{username} &>/dev/null || :
test "$1" != 0 || /usr/sbin/fedora-groupdel %{username} &>/dev/null || :

%pre milter
/usr/sbin/fedora-groupadd 5 -r %milteruser &>/dev/null || :
/usr/sbin/fedora-useradd  5 -r -s /sbin/nologin -d %milterstatedir -M \
                            -c 'Clamav Milter User' -g %milteruser %milteruser &>/dev/null || :

%post milter
/sbin/chkconfig --add clamav-milter
/sbin/chkconfig --add clamd.milter

%preun milter
test "$1" != 0 || %{_initrddir}/clamav-milter stop &>/dev/null || :
test "$1" != 0 || %{_initrddir}/clamd.milter  stop &>/dev/null || :
test "$1" != 0 || /sbin/chkconfig --del clamav-milter
test "$1" != 0 || /sbin/chkconfig --del clamd.milter

%postun milter
test "$1" != 0 || /usr/sbin/fedora-userdel  %{milteruser} &>/dev/null || :
test "$1" != 0 || /usr/sbin/fedora-groupdel %{milteruser} &>/dev/null || :
test "$1"  = 0 || %{_initrddir}/clamd.milter  condrestart >/dev/null || :
test "$1"  = 0 || %{_initrddir}/clamav-milter condrestart >/dev/null || :


%post   lib -p /sbin/ldconfig
%postun lib -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc AUTHORS BUGS COPYING ChangeLog FAQ NEWS TODO
%doc docs/*.pdf
%doc docs/html docs/DMS docs/FreeBSD-HowTo
%lang(fr) %doc docs/French
%lang(ja) %doc docs/Japanese
%lang(pl) %doc docs/Polish
%lang(pt) %doc docs/Portugese
%lang(es) %doc docs/Spanish
%lang(tr) %doc docs/Turkish
%doc %{_mandir}/man[15]/*
%{_bindir}/*
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

## -----------------------

%files data
%defattr(-,%{username},%{username},-)
%dir %{homedir}
%config %verify(not size md5 mtime) %{homedir}/*.cvd

## -----------------------

%files update
%defattr(-,root,root,-)
%_bindir/freshclam
%_mandir/man1/freshclam*
%config(noreplace) %verify(not mtime) %_sysconfdir/freshclam.conf
%config(noreplace) %verify(not mtime) %_sysconfdir/cron.d/*
%config(noreplace) %verify(not mtime) %_sysconfdir/logrotate.d/*

%ghost %attr(0664,root,%{username}) %verify(not size md5 mtime) %{freshclamlog}

## -----------------------

%files server
%defattr(-,root,root,-)
%doc _doc_server/*
%doc etc/clamav.conf
%doc %{_mandir}/man8/*
%{_sbindir}/*
%config %{_initrddir}/clamd-wrapper
%dir %{_sysconfdir}/clamd.d

%exclude %_sbindir/*milter*
%exclude %_mandir/man8/clamav-milter*

## -----------------------

%files milter
%defattr(-,root,root,-)
%doc clamav-milter/INSTALL
%_sbindir/*milter*
%_mandir/man8/clamav-milter*
%config %{_initrddir}/clamd.milter
%config %{_initrddir}/clamav-milter
%config(noreplace) %verify(not mtime) %{_sysconfdir}/clamd.d/milter.conf
%config(noreplace) %verify(not mtime) %{_sysconfdir}/sysconfig/clamav-milter
%attr(0700,%milteruser,%milteruser) %dir %milterclamddir
%attr(0700,%milteruser,%milteruser) %dir %milterstatedir
%ghost %milterclamddir/*
%ghost %milterstatedir/*
%ghost %attr(0620,root,%milteruser) %verify(not size md5 mtime) %milterlog


%changelog
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
