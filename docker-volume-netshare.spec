%global import_path     github.com/ContainX/docker-volume-netshare
%global commit          764b18ec6816085deb8edcc5c594e02cdd805cb3            
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

%global _dwz_low_mem_die_limit 0

Name:       docker-volume-netshare
Version:	0.34
Release:	0.1.git%{shortcommit}%{?dist}
Summary:	Mount NFS v3/4, AWS EFS or CIFS inside your docker containers.

Group:		Unspecified
License:	ASL 2.0
URL:		https://github.com/ContainX/docker-volume-netshare/
Source0:	https://github.com/ContainX/docker-volume-netshare/archive/v0.34.tar.gz

%{?systemd_requires}
BuildRequires:  compiler(go-compiler) systemd git
Requires:	docker

%description
This is a docker plugin which enables these volume types
to be directly mounted within a container.

%prep
%setup -q
#cd docker-volume-netshare-0.34/

%build
#cd docker-volume-netshare-0.34/
#pwd
mkdir -p src/github.com/ContainX bin
ln -snf ../../../ src/github.com/ContainX/docker-volume-netshare
#export GOPATH=$PWD GOBIN=$PWD/bin

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
mkdir -p %{buildroot}%{_bindir}
install bin/docker-volume-netshare %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}
cp -pr support/systemd/lib/systemd/system/* %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
cp -pr support/systemd/etc/* %{buildroot}%{_sysconfdir}/sysconfig
mkdir -p %{buildroot}%{_docdir}/%{name}
install LICENSE %{buildroot}%{_docdir}/%{name}/

%files
%doc %{_docdir}/%{name}/LICENSE
%{_bindir}/*
%{_sysconfdir}/sysconfig/*
%{_unitdir}

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%changelog

