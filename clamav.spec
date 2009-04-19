#global snapshot	rc1

## Fedora Extras specific customization below...
%bcond_without       	fedora
%bcond_without		upstart
%bcond_with		unrar
##

%global username	clamav
%global homedir		%_var/lib/clamav
%global freshclamlog	%_var/log/freshclam.log
%global milteruser	clamilt
%global milterlog	%_var/log/clamav-milter.log
%global milterstatedir	%_var/run/clamav-milter
%global pkgdatadir	%_datadir/%name

%global scanuser	clamscan
%global scanstatedir	%_var/run/clamd.scan

%{!?release_func:%global release_func() %1%{?dist}}

Summary:	End-user tools for the Clam Antivirus scanner
Name:		clamav
Version:	0.95.1
Release:	%release_func 3%{?snapshot:.%snapshot}

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
Patch24:	clamav-0.92-private.patch
Patch25:	clamav-0.92-open.patch
Patch26:	clamav-0.95-cliopts.patch
Patch27:	clamav-0.95rc1-umask.patch
BuildRoot:	%_tmppath/%name-%version-%release-root
Requires:	clamav-lib = %version-%release
Requires:	data(clamav)
BuildRequires:	zlib-devel bzip2-devel gmp-devel curl-devel
BuildRequires:	ncurses-devel
BuildRequires:	%_includedir/tcpd.h
BuildRequires:	bc

%package filesystem
Summary:	Filesystem structure for clamav
Group:		Applications/File
BuildArch:	noarch
Provides:	user(%username)  = 4
Provides:	group(%username) = 4
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
BuildArch:	noarch
Requires(pre):		clamav-filesystem = %version-%release
Requires(postun):	clamav-filesystem = %version-%release
Provides:		data(clamav) = full
Conflicts:		data(clamav) < full
Conflicts:		data(clamav) > full

%package data-empty
Summary:	Empty data package for the Clam Antivirus scanner
Group:		Applications/File
BuildArch:	noarch
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
Requires:	data(clamav)
Requires:	clamav-filesystem = %version-%release
Requires:	clamav-lib        = %version-%release

%package server-sysvinit
Summary:	SysV initscripts for clamav server
Group:		System Environment/Daemons
BuildArch:	noarch
Provides:	init(clamav-server) = sysv
Requires:	clamav-server = %version-%release
Requires(pre):		%_initrddir
Requires(postun):	%_initrddir
Provides:	clamav-server-sysv = %version-%release
Obsoletes:	clamav-server-sysv < %version-%release


%package scanner
Summary:	Clamav scanner daemon
Group:		System Environment/Daemons
BuildArch:	noarch
Requires:	init(clamav-scanner)
Provides:	user(%scanuser)  = 49
Provides:	group(%scanuser) = 49
Requires:	clamav-server = %version-%release

%package scanner-sysvinit
Summary:	SysV initscripts for clamav scanner daemon
Group:		System Environment/Daemons
BuildArch:	noarch
Provides:	init(clamav-scanner) = sysv
Requires:	clamav-server-sysvinit = %version-%release
Requires:	clamav-scanner = %version-%release
Requires(pre):		%_initrddir
Requires(postun):	%_initrddir initscripts
Requires(post):		chkconfig
Requires(preun):	chkconfig initscripts

%package scanner-upstart
Summary:	Upstart initscripts for clamav scanner daemon
Group:		System Environment/Daemons
BuildArch:	noarch
Source410:	clamd.scan.upstart
Provides:	init(clamav-scanner) = upstart
Requires:	clamav-scanner = %version-%release
# implicates a conflict with upstart 0.5+
Requires(pre):		/etc/event.d	
Requires(post):		/usr/bin/killall
Requires(postun):	/sbin/initctl


%package milter
Summary:	Milter module for the Clam Antivirus scanner
Group:		System Environment/Daemons
Source300:	README.fedora
Requires:	init(clamav-milter)
BuildRequires:	sendmail-devel
BuildRequires:	fedora-usermgmt-devel
Provides:	user(%milteruser)  = 5
Provides:	group(%milteruser) = 5
Requires(post):	coreutils
%{?FE_USERADD_REQ}

Provides:	milter(clamav) = sendmail
Provides:	milter(clamav) = postfix

Provides:	clamav-milter-core = %version-%release
Obsoletes:	clamav-milter-core < %version-%release
Provides:	clamav-milter-sendmail = %version-%release
Obsoletes:	clamav-milter-sendmail < %version-%release

%package milter-sysvinit
Summary:	SysV initscripts for the clamav sendmail-milter
Group:		System Environment/Daemons
BuildArch:	noarch
Source320:	clamav-milter.sysv
Provides:	init(clamav-milter) = sysvinit
Requires:	clamav-milter = %version-%release
Requires(post):		user(%milteruser) clamav-milter
Requires(preun):	user(%milteruser) clamav-milter
Requires(pre):		%_initrddir
Requires(postun):	%_initrddir initscripts
Requires(post):		chkconfig
Requires(preun):	chkconfig initscripts
Provides:		clamav-milter-sysv = %version-%release
Obsoletes:		clamav-milter-sysv < %version-%release

%package milter-upstart
Summary:	Upstart initscripts for the clamav sendmail-milter
Group:		System Environment/Daemons
BuildArch:	noarch
Source310:	clamav-milter.upstart
Provides:	init(clamav-milter) = upstart
Requires:	clamav-milter = %version-%release
# implicates a conflict with upstart 0.5+
Requires(pre):		/etc/event.d	
Requires(post):		/usr/bin/killall
Requires(postun):	/sbin/initctl


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


%description server-sysvinit
SysV initscripts template for the clamav server


%description scanner
This package contains a generic system wide clamd service which is
e.g. used by the clamav-milter package.

%description scanner-sysvinit
The SysV initscripts for clamav-scanner.

%description scanner-upstart
The Upstart initscripts for clamav-scanner.


%description milter
This package contains files which are needed to run the clamav-milter.

%description milter-sysvinit
The SysV initscripts for clamav-milter.

%description milter-upstart
The Upstart initscripts for clamav-milter.

## ------------------------------------------------------------

%prep
%setup -q -n %{name}-%{version}%{?snapshot}

%patch24 -p1 -b .private
%patch25 -p1 -b .open
%patch26 -p1 -b .cliopts
%patch27 -p1 -b .umask

install -p -m0644 %SOURCE300 clamav-milter/

mkdir -p libclamunrar{,_iface}
%{!?with_unrar:touch libclamunrar/{Makefile.in,all,install}}

sed -ri \
    -e 's!^(#?LogFile ).*!\1/var/log/clamd.<SERVICE>!g' \
    -e 's!^(#?LocalSocket ).*!\1/var/run/clamd.<SERVICE>/clamd.sock!g' \
    -e 's!^(#?PidFile ).*!\1/var/run/clamd.<SERVICE>/clamd.pid!g' \
    -e 's!^#?(User ).*!\1<USER>!g' \
    -e 's!^#?(AllowSupplementaryGroups|LogSyslog).*!\1 yes!g' \
    -e 's! /usr/local/share/clamav,! %homedir,!g' \
    etc/clamd.conf

sed -ri -e 's!^#(UpdateLogFile )!\1!g;' etc/freshclam.conf


## ------------------------------------------------------------

%build
CFLAGS="$RPM_OPT_FLAGS -Wall -W -Wmissing-prototypes -Wmissing-declarations -std=gnu99"
export LDFLAGS='-Wl,--as-needed'
# HACK: remove me, when configure uses $LIBS instead of $LDFLAGS for milter check
export LIBS='-lmilter -lpthread'
# IPv6 check is buggy and does not work when there are no IPv6 interface on build machine
export have_cv_ipv6=yes
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
	${RPM_BUILD_ROOT}%_sysconfdir/{mail,clamd.d,cron.d,logrotate.d,sysconfig,event.d} \
	${RPM_BUILD_ROOT}%_var/log \
	${RPM_BUILD_ROOT}%milterstatedir \
	${RPM_BUILD_ROOT}%pkgdatadir/template \
	${RPM_BUILD_ROOT}%_initrddir \
	${RPM_BUILD_ROOT}%homedir \
	${RPM_BUILD_ROOT}%scanstatedir

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


### The scanner stuff
sed -e 's!<SERVICE>!scan!g;s!<USER>!%scanuser!g' \
    etc/clamd.conf > $RPM_BUILD_ROOT%_sysconfdir/clamd.d/scan.conf

sed -e 's!<SERVICE>!scan!g;' $RPM_BUILD_ROOT%pkgdatadir/template/clamd.init \
    > $RPM_BUILD_ROOT%_initrddir/clamd.scan

install -p -m 644 %SOURCE410 $RPM_BUILD_ROOT%_sysconfdir/event.d/clamd.scan

touch $RPM_BUILD_ROOT%scanstatedir/clamd.sock


### The milter stuff
sed -r \
    -e 's!^#?(User).*!\1 %milteruser!g' \
    -e 's!^#?(AllowSupplementaryGroups|LogSyslog) .*!\1 yes!g' \
    -e 's! /tmp/clamav-milter.socket! %milterstatedir/clamav-milter.socket!g' \
    -e 's! /var/run/clamav-milter.pid! %milterstatedir/clamav-milter.pid!g' \
    -e 's! /tmp/clamav-milter.log! %milterlog!g' \
    etc/clamav-milter.conf > $RPM_BUILD_ROOT%_sysconfdir/mail/clamav-milter.conf

install -p -m 644 %SOURCE310 $RPM_BUILD_ROOT%_sysconfdir/event.d/clamav-milter
install -p -m 755 %SOURCE320 $RPM_BUILD_ROOT%_initrddir/clamav-milter


rm -f $RPM_BUILD_ROOT%_sysconfdir/clamav-milter.conf
touch $RPM_BUILD_ROOT{%milterstatedir/clamav-milter.socket,%milterlog}

%{!?with_upstart:rm -rf $RPM_BUILD_ROOT%_sysconfdir/event.d}

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


%pre scanner
%__fe_groupadd 49 -r %scanuser &>/dev/null || :
%__fe_useradd  49 -r -s /sbin/nologin -d / -M \
                 -g %scanuser %scanuser &>/dev/null || :

%postun scanner
%__fe_userdel  %scanuser &>/dev/null || :
%__fe_groupdel %scanuser &>/dev/null || :


%post scanner-sysvinit
/sbin/chkconfig --add clamd.scan

%preun scanner-sysvinit
test "$1" != 0 || %_initrddir/clamd.scan stop &>/dev/null || :
test "$1" != 0 || /sbin/chkconfig --del clamd.scan

%postun scanner-sysvinit
test "$1"  = 0 || %_initrddir/clamd.scan condrestart >/dev/null || :


%post scanner-upstart
/usr/bin/killall -u %scanuser clamd 2>/dev/null || :

%preun scanner-upstart
test "$1" != "0" || /sbin/initctl -q stop clamd.scan || :



%post update
test -e %freshclamlog || {
	touch %freshclamlog
	%__chmod 0664 %freshclamlog
	%__chown root:%username %freshclamlog
}

%pre milter
%__fe_groupadd 5 -r %milteruser &>/dev/null || :
%__fe_useradd  5 -r -s /sbin/nologin -d %milterstatedir -M \
                 -c 'Clamav Milter User' -g %milteruser %milteruser &>/dev/null || :

%post milter
test -e %milterlog || {
	touch %milterlog
	chmod 0620             %milterlog
	chown root:%milteruser %milterlog
}

%postun milter
%__fe_userdel  %milteruser &>/dev/null || :
%__fe_groupdel %milteruser &>/dev/null || :


%post milter-sysvinit
/sbin/chkconfig --add clamav-milter

%preun milter-sysvinit
test "$1" != 0 || %_initrddir/clamav-milter stop &>/dev/null || :
test "$1" != 0 || /sbin/chkconfig --del clamav-milter

%postun milter-sysvinit
test "$1"  = 0 || %_initrddir/clamav-milter condrestart >/dev/null || :


%post milter-upstart
/usr/bin/killall -u %milteruser clamav-milter 2>/dev/null || :

%preun milter-upstart
test "$1" != "0" || /sbin/initctl -q stop clamav-milter || :


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


%files server-sysvinit
%defattr(-,root,root,-)
%_initrddir/clamd-wrapper


## -----------------------

%files scanner
%defattr(-,root,root,-)
%dir %attr(0710,%scanuser,%scanuser) %scanstatedir
%config(noreplace) %_sysconfdir/clamd.d/scan.conf
%ghost %scanstatedir/clamd.sock

%files scanner-sysvinit
%attr(0755,root,root) %config %_initrddir/clamd.scan

%if 0%{?with_upstart:1}
%files scanner-upstart
%defattr(-,root,root,-)
%config(noreplace) %_sysconfdir/event.d/clamd.scan
%endif

## -----------------------

%files milter
%defattr(-,root,root,-)
%doc clamav-milter/README.fedora
%_sbindir/*milter*
%_mandir/man8/clamav-milter*
%config(noreplace) %_sysconfdir/mail/clamav-milter.conf
%ghost %attr(0620,root,%milteruser) %verify(not size md5 mtime) %milterlog
%attr(0710,%milteruser,%milteruser) %dir %milterstatedir
%ghost %milterstatedir/*

%files milter-sysvinit
%defattr(-,root,root,-)
%config %_initrddir/clamav-milter

%if 0%{?with_upstart:1}
%files milter-upstart
%defattr(-,root,root,-)
%config(noreplace) %_sysconfdir/event.d/clamav-milter
%endif


%changelog
* Sun Apr 19 2009 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.95.1-3
- fixed '--without upstart' operation

* Wed Apr 15 2009 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.95.1-2
- added '%%bcond_without upstart' conditional to ease skipping of
  -upstart subpackage creation e.g. on EL5 systems
- fixed Provides/Obsoletes: typo in -milter-sysvinit subpackage which
  broke update path

* Fri Apr 10 2009 Robert Scheck <robert@fedoraproject.org> - 0.95.1-1
- Upgrade to 0.95.1 (#495039)

* Wed Mar 25 2009 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.95-1
- updated to final 0.95
- added ncurses-devel (-> clamdtop) BR
- enforced IPv6 support

* Sun Mar  8 2009 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.95-0.1.rc1
- updated to 0.95rc1
- added -upstart subpackages
- renamed -sysv to -sysvinit to make -upstart win the default dep resolving
- reworked complete milter stuff
- added -scanner subpackage which contains a preconfigured daemon
  (e.g. for use by -milter)
- moved %%changelog entries from 2006 and before into ChangeLog-rpm.old

* Wed Feb 25 2009 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.94.2-3
- made some subpackages noarch
- fixed typo in SysV initscript which removes 'touch' file (#473513)

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.94.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Dec 02 2008 Robert Scheck <robert@fedoraproject.org> - 0.94.2-1
- Upgrade to 0.94.2 (#474002)

* Wed Nov 05 2008 Robert Scheck <robert@fedoraproject.org> - 0.94.1-1
- Upgrade to 0.94.1

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
