%global debug_package   %{nil}
%global provider        github
%global provider_tld    com
%global project         cpuguy83
%global repo            go-md2man
%global import_path     %{provider}.%{provider_tld}/%{project}/%{repo}
%global commit          1d903dcb749992f3741d744c0f8376b4bd7eb3e1
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

%global san_commit      8e87604bec3c645a4eeaee97dfec9f25811ff20d
%global san_shortcommit %(c=%{san_commit}; echo ${c:0:7})
%global san_repo        sanitized_anchor_name

%global bl_commit       77efab57b2f74dd3f9051c79752b2e8995c8b789
%global bl_shortcommit  %(c=%{bl_commit}; echo ${c:0:7})
%global bl_repo         blackfriday

Name:           golang-%{provider}-%{project}-%{repo}
Version:        1.0.7
Release:        1%{?dist}
Summary:        Process markdown into manpages
License:        MIT
URL:            https://%{import_path}
Source0:        https://%{import_path}/archive/%{commit}/%{repo}-%{shortcommit}.tar.gz
Source1:        https://github.com/shurcooL/%{san_repo}/archive/%{san_commit}/%{san_repo}-%{san_shortcommit}.tar.gz
Source2:        https://github.com/russross/%{bl_repo}/archive/%{bl_commit}/%{bl_repo}-%{bl_shortcommit}.tar.gz
Provides:       %{repo} = %{version}-%{release}
%if 0%{?centos} || 0%{?fedora}
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 %{arm} aarch64 ppc64le s390x}
%else
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:x86_64 %{arm} aarch64 ppc64le s390x}
%endif
BuildRequires:  golang >= 1.2.1-3

%description
%{repo} is a golang tool using blackfriday to process markdown into
manpages.

%prep
%setup -q -n %{san_repo}-%{san_commit} -T -b 1
%setup -q -n %{bl_repo}-%{bl_commit} -T -b 2
%setup -qn %{repo}-%{commit}

mkdir -p Godeps/_workspace/src/github.com/shurcooL/%{san_repo}
cp -r ../%{san_repo}-%{san_commit}/* Godeps/_workspace/src/github.com/shurcooL/%{san_repo}/.
mkdir -p Godeps/_workspace/src/github.com/russross/%{bl_repo}
cp -r ../%{bl_repo}-%{bl_commit}/* Godeps/_workspace/src/github.com/russross/%{bl_repo}/.

%build
mkdir -p _build/src/%{provider}.%{provider_tld}/%{project}
ln -s $(pwd) ./_build/src/%{import_path}

export GOPATH=$(pwd)/_build:$(pwd)/Godeps/_workspace

pushd $(pwd)/_build/src
go build -v %{import_path}
popd

%install
# install go-md2man binary
install -d %{buildroot}%{_bindir}
install -p -m 755 ./_build/src/%{repo} %{buildroot}%{_bindir}

%files
%doc README.md
%{_bindir}/%{repo}

%changelog
* Wed May 27 2020 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.7-1
- bump to v1.0.7
- RE: #1616184

* Wed Mar 15 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.4-4
- Resolves: #1344553 - build only for go_arches
- update ambiguous changelog in previous entry
- update go_arches definition

* Wed Mar 15 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.4-3
- Resolves: #1344553 - build for all available arches (previous build didn't
fix it)

* Tue Mar 14 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.4-2
- Resolves: #1344553 - build for 7.4

* Tue Dec 15 2015 jchaloup <jchaloup@redhat.com> - 1.0.4-1
- Rebase to 1.0.4
  Deps import separatelly, not in one tarball
  resolves: #1291380

* Wed Jun 17 2015 jchaloup <jchaloup@redhat.com> - 1-5
- Update the spec file for RHEL
- Remove devel subpackage
- Bundle github.com/russross/blackfriday and github.com/shurcooL/sanitized_anchor_name into tarball
- Use bundled dependencies to build md2man
  resolves: #1211312

* Wed Feb 25 2015 jchaloup <jchaloup@redhat.com> - 1-4
- Bump to upstream 2831f11f66ff4008f10e2cd7ed9a85e3d3fc2bed
  related: #1156492

* Wed Feb 25 2015 jchaloup <jchaloup@redhat.com> - 1-3
- Add commit and shortcommit global variable
  related: #1156492

* Mon Oct 27 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1-2
- Resolves: rhbz#1156492 - initial fedora upload
- quiet setup
- no test files, disable check

* Thu Sep 11 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1-1
- Initial package
