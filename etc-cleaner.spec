%global commit  @commit@
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           etc-cleaner
Version:        0
Release:        1.%{shortcommit}%{?dist}
Summary:        /etc config files GUI maintenance tool

Group:          Applications/System
License:        GPLv2
URL:            https://github.com/leamas/etc-cleaner
Source0:        %{url}/archive/%{commit}/%{name}-%{version}-%{shortcommit}.tar.gz
Requires:       sudo gtk3
Requires:       %{name}-main = %version}-%{release}
Requires:       %{name}-attach-term = %version}-%{release}

BuildRequires:  python2-devel


%description
A simple GUI application intended to make it easier to maintain the
configuration files in /etc. The problem is basically about merging
the local changes with the changes made by the package installers
when updating.

The app first lists all changes done so far (i. e., files having any
.rpmnew or .rpmsave variants). When clicking on such a change there is
a window where you can select which variant to use, view it, merge it
or just show the diff.

This is a meta-package. There should be no need to install anything but
this package.


%package attach-term
Summary:        Run argument with stdout attached to a pty

%description attach-term
Runs it's single argument with stdout redirected to a pty. This is a sudo
walk-around to to enable otherwise disabled tickets when invoking sudo from
a GUI program.


%package main
Summary:      Python and data noarch etc-cleaner components.
BuildArch:    noarch

%description main
etc-cleaner noarch components separate package.


%prep
%setup -qn %{name}-%{commit}


%build


%install
make DESTDIR=%{buildroot} install-usr


%files attach-term
%{_bindir}/attach_term

%files
%doc README.md

%files main
%{python_sitelib}/etc_cleaner
%{python_sitelib}/etc_cleaner-*egg-info
%{_bindir}/etc-cleaner
%{_mandir}/man8/etc-cleaner.8*
%{_datadir}/etc-cleaner
%{_datadir}/applications/etc-cleaner.desktop
%{_datadir}/icons/hicolor/*/apps/etc-cleaner.png
/etc/etc-cleaner


%changelog
* Mon Sep 30 2013 Alec leamas <leamas@nowhere.net> - 0-1.b9822216
- Initial package
