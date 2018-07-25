%global import_path     github.com/ContainX/docker-volume-netshare
%global commit          359f4a98948711b4d247d4dec86a5e2e75dc591d            
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

%global _dwz_low_mem_die_limit 0

%global use_systemd 1

%{!?gobuild: %define gobuild(o:) go build -compiler gc -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n')" -a -v -x %{?**}; }

%if 0%{?rhel} && 0%{?rhel} < 7
%global use_systemd 0
%endif

Name:       docker-volume-netshare
Version:	0.35
Release:	0.2.git%{shortcommit}%{?dist}
Summary:	Mount NFS v3/4, AWS EFS or CIFS inside your docker containers.

Group:		Unspecified
License:	ASL 2.0
URL:		https://github.com/ContainX/docker-volume-netshare/
Source0:	https://github.com/ContainX/docker-volume-netshare/archive/v0.35.tar.gz

%if 0%{?use_systemd}
%{?systemd_requires}
BuildRequires: systemd
%endif

BuildRequires:  golang-bin git
Requires:	docker

%description
This is a docker plugin which enables these volume types
to be directly mounted within a container.

%prep
%setup -q

%build
mkdir -p src/github.com/ContainX bin
ln -snf ../../../ src/github.com/ContainX/docker-volume-netshare

%if ! 0%{?with_bundled}
export GOPATH=$(pwd):%{gopath}
export GOBIN=$(pwd)/bin
%else
echo "Unable to build from bundled deps. No Godeps nor vendor directory"
exit 1
%endif

go get
%gobuild -o bin/docker-volume-netshare %{import_path}

%install
mkdir -p %{buildroot}%{_docdir}/%{name}
install LICENSE %{buildroot}%{_docdir}/%{name}/
mkdir -p %{buildroot}%{_bindir}
install bin/docker-volume-netshare %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}
%if 0%{?use_systemd}
cp -pr support/systemd/lib/systemd/system/* %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_sysconfdir}
cp -pr support/systemd/etc/* %{buildroot}%{_sysconfdir}
%else
mkdir -p %{buildroot}%{_initddir}
cp -pr support/sysvinit-debian/etc/init.d/* %{buildroot}%{_initddir}
mkdir -p %{buildroot}%{_sysconfdir}/default
cp -pr support/sysvinit-debian/etc/default/* %{buildroot}%{_sysconfdir}/default
%endif

%files
%doc %{_docdir}/%{name}/LICENSE
%{_bindir}/*
%if 0%{?use_systemd}
%{_sysconfdir}/*
%{_unitdir}/*
%else
%{_initddir}/*
%{_sysconfdir}/default/*
%endif

%post
%if 0%{?use_systemd}
%systemd_post %{name}.service
%else
/sbin/chkconfig --add %{name}
%endif

%preun
%if 0%{?use_systemd}
%systemd_preun %{name}.service
%else
if [ $1 = 0 ] ; then
/sbin/service %{name} stop >/dev/null 2>&1 || :
/sbin/chkconfig --del %{name}
fi
%endif

%postun
%if 0%{?use_systemd}
%systemd_postun_with_restart %{name}.service
%else
if [ "$1" -ge "1" ] ; then
/sbin/service %{name} restart >/dev/null 2>&1 || :
fi
%endif

%changelog

