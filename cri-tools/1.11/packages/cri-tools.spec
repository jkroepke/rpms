%global with_bundled 1
%global with_debug 1
%global with_check 0

%if 0%{?with_debug}
%global _find_debuginfo_dwz_opts %{nil}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

# %if ! 0% {?gobuild:1}
%define gobuild(o:) go build -tags="$BUILDTAGS selinux seccomp" -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n')" -a -v -x %{?**};
#% endif

%global provider        github
%global provider_tld    com
%global project         kubernetes-sigs
%global repo            cri-tools
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}
%global commit          edabfb531c362e664c574fa651419d55815f860a
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

Name:           cri-tools
Version:        1.11.1
Release:        2.rhaos3.11.git%{shortcommit}%{?dist}
Summary:        CLI and validation tools for Container Runtime Interface
License:        ASL 2.0
URL:            https://%{provider_prefix}
Source0:        https://%{provider_prefix}/archive/%{commit}/%{repo}-%{shortcommit}.tar.gz
# no ppc64
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 aarch64 %{arm} ppc64le s390x}
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}
BuildRequires:  glibc-static
BuildRequires:  git
BuildRequires:  go-md2man
Provides:       crictl = %{version}-%{release}

# vendored libraries
# awk '{print "Provides: bundled(golang("$1")) = "$2}' vendor.conf | sort
# [thanks to Carl George <carl@george.computer> for containerd.spec]
Provides: bundled(golang(github.com/Azure/go-ansiterm)) = 19f72df4d05d31cbe1c56bfc8045c96babff6c7e
Provides: bundled(golang(github.com/docker/docker)) = 4f3616fb1c112e206b88cb7a9922bf49067a7756
Provides: bundled(golang(github.com/docker/go-units)) = 9e638d38cf6977a37a8ea0078f3ee75a7cdb2dd1
Provides: bundled(golang(github.com/docker/spdystream)) = 449fdfce4d962303d702fec724ef0ad181c92528
Provides: bundled(golang(github.com/fsnotify/fsnotify)) = f12c6236fe7b5cf6bcf30e5935d08cb079d78334
Provides: bundled(golang(github.com/ghodss/yaml)) = 73d445a93680fa1a78ae23a5839bad48f32ba1ee
Provides: bundled(golang(github.com/gogo/protobuf)) = c0656edd0d9eab7c66d1eb0c568f9039345796f7
Provides: bundled(golang(github.com/golang/glog)) = 44145f04b68cf362d9c4df2182967c2275eaefed
Provides: bundled(golang(github.com/golang/protobuf)) = b4deda0973fb4c70b50d226b1af49f3da59f5265
Provides: bundled(golang(github.com/google/gofuzz)) = 44d81051d367757e1c7c6a5a86423ece9afcf63c
Provides: bundled(golang(github.com/json-iterator/go)) = f2b4162afba35581b6d4a50d3b8f34e33c144682
Provides: bundled(golang(github.com/mitchellh/go-wordwrap)) = ad45545899c7b13c020ea92b2072220eefad42b8
Provides: bundled(golang(github.com/modern-go/concurrent)) = bacd9c7ef1dd9b15be4a9909b8ac7a4e313eec94
Provides: bundled(golang(github.com/modern-go/reflect2)) = 05fbef0ca5da472bbf96c9322b84a53edc03c9fd
Provides: bundled(golang(github.com/onsi/ginkgo)) = 67b9df7f55fe1165fd9ad49aca7754cce01a42b8
Provides: bundled(golang(github.com/onsi/gomega)) = d59fa0ac68bb5dd932ee8d24eed631cdd519efc3
Provides: bundled(golang(github.com/opencontainers/selinux)) = 4a2974bf1ee960774ffd517717f1f45325af0206
Provides: bundled(golang(github.com/pborman/uuid)) = ca53cad383cad2479bbba7f7a1a05797ec1386e4
Provides: bundled(golang(github.com/sirupsen/logrus)) = 89742aefa4b206dcf400792f3bd35b542998eb3b
Provides: bundled(golang(github.com/urfave/cli)) = 8e01ec4cd3e2d84ab2fe90d8210528ffbb06d8ff
Provides: bundled(golang(golang.org/x/crypto)) = 49796115aa4b964c318aad4f3084fdb41e9aa067
Provides: bundled(golang(golang.org/x/net)) = 1c05540f6879653db88113bc4a2b70aec4bd491f
Provides: bundled(golang(golang.org/x/sys)) = 95c6576299259db960f6c5b9b69ea52422860fce
Provides: bundled(golang(golang.org/x/text)) = b19bf474d317b857955b12035d2c5acb57ce8b01
Provides: bundled(golang(golang.org/x/time)) = f51c12702a4d776e4c1fa9b0fabab841babae631
Provides: bundled(golang(google.golang.org/genproto)) = 09f6ed296fc66555a25fe4ce95173148778dfa85
Provides: bundled(golang(google.golang.org/grpc)) = v1.7.5
Provides: bundled(golang(gopkg.in/inf.v0)) = v0.9.0
Provides: bundled(golang(gopkg.in/yaml.v2)) = 670d4cfef0544295bc27a114dbac37980d83185a
Provides: bundled(golang(k8s.io/api)) = 783dfbe86ff74ef4a6e1243688e1585ac243f8e7
Provides: bundled(golang(k8s.io/apimachinery)) = 5a8013207d0d28c7fe98193e5b6cdbf92e98a000
Provides: bundled(golang(k8s.io/client-go)) = 8d6e3480fc03b7337a24f349d35733190655e2ad
Provides: bundled(golang(k8s.io/kubernetes)) = 3abba25160590921fec61236ba012a8bbd757d6c
Provides: bundled(golang(k8s.io/utils)) = 258e2a2fa64568210fbd6267cf1d8fd87c3cb86e

%description
%{summary}

%prep
%autosetup -Sgit -n %{repo}-%{commit}

%build
mkdir _build
pushd _build
mkdir -p src/%{provider}.%{provider_tld}/%{project}
ln -s ../../../../ src/%{import_path}
popd
ln -s vendor src
export GOPATH=$(pwd)/_build:$(pwd)

GOPATH=$GOPATH %gobuild -o bin/crictl %{import_path}/cmd/crictl
go-md2man -in docs/crictl.md -out docs/crictl.1

%install
# install binaries
install -dp %{buildroot}%{_bindir}
install -p -m 755 ./bin/crictl %{buildroot}%{_bindir}

# install manpage
install -dp %{buildroot}%{_mandir}/man1
install -p -m 644 docs/crictl.1 %{buildroot}%{_mandir}/man1

%check

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files
%license LICENSE
%doc CHANGELOG.md CONTRIBUTING.md OWNERS README.md RELEASE.md code-of-conduct.md
%doc docs/{benchmark.md,roadmap.md,validation.md}
%{_bindir}/crictl
%{_mandir}/man1/crictl*

%changelog
* Fri Sep 14 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.11.1-1.rhaos3.11.gitedabfb5
- built release-1.11 commit edabfb5
- use correct version number

* Mon Jul 02 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-6.rhaos3.11.git78ec590
- import spec from rhaos3.10
- built release-1.11 commit 78ec590

* Wed May 16 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-5.rhaos3.10.git2e22a75
- Resolves: #1572795 - build for all arches
- From: Yaakov Selkowitz <yselkowi@redhat.com>

* Tue May 15 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-4.rhaos3.10.git2e22a75
- built commit 2e22a75
- include rhaos version in release tag

* Sun Apr 22 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-3.gitf37a5a1
- built commit f37a5a1
- critest doesn't build, skipped for now

* Wed Feb 07 2018 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.0.0-2.alpha.0.git653cc8c
- include critest binary

* Wed Feb 07 2018 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.0.0-1.alpha.0.gitf1a58d6
- First package for Fedora
