%global with_debug 1
%global with_check 0

%if 0%{?with_debug}
%global _find_debuginfo_dwz_opts %{nil}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package %{nil}
%endif

%define gobuild(o:) go build -buildmode pie -compiler gc -tags="rpm_crashtraceback ${BUILDTAGS:-}" -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n') -extldflags '%__global_ldflags'" -a -v -x %{?**};

%global provider github
%global provider_tld com
%global project cri-o
%global repo %{project}
# https://github.com/cri-o/cri-o
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path %{provider_prefix}
%global commit0 54f9e69c416b63218dafc3d39c3c7274874616bc
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global git0 https://%{import_path}

%global service_name crio

Name: %{repo}
Version: 1.11.16
Release: 0.16.rhaos3.11.git%{shortcommit0}%{?dist}
Summary: Kubernetes Container Runtime Interface for OCI-based containers
License: ASL 2.0
URL: %{git0}
Source0: %{git0}/archive/%{commit0}/%{name}-%{shortcommit0}.tar.gz
Source3: %{service_name}-network.sysconfig
Source4: %{service_name}-storage.sysconfig
# cgo LDFLAGS patch only for rhel
%if ! 0%{?fedora}
Patch0: cri-o-1792243.patch
%endif
# https://bugzilla.redhat.com/show_bug.cgi?id=1796066
Patch1: cri-o-1796066.patch
# related bug: https://bugzilla.redhat.com/show_bug.cgi?id=1955657
# patch:       backported.patch
Patch2: cri-o-1955657.patch

# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires: %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}
BuildRequires: btrfs-progs-devel
BuildRequires: git
BuildRequires: glib2-devel
BuildRequires: glibc-static
BuildRequires: go-md2man
BuildRequires: gpgme-devel
BuildRequires: libassuan-devel
BuildRequires: libseccomp-devel
BuildRequires: pkgconfig(systemd)
BuildRequires: device-mapper-devel
Requires(pre): container-selinux
Requires: skopeo-containers >= 1:0.1.24-3
Requires: runc >= 1.0.0-16
Obsoletes: ocid <= 0.3
Provides: ocid = %{version}-%{release}
Provides: %{service_name} = %{version}-%{release}
Requires: containernetworking-plugins >= 0.7.0-101

%description
%{summary}

%package cni-configs
Summary: CNI config files for %{name}
BuildArch: noarch

%description cni-configs
%{summary}

%prep
%autosetup -Sgit -n %{name}-%{commit0}
sed -i '/strip/d' pause/Makefile
sed -i 's/install.config: crio.conf/install.config:/' Makefile
sed -i 's/%{version}/%{version}-%{release}/' version/version.go

%build
mkdir _output
pushd _output
mkdir -p src/%{provider}.%{provider_tld}/{%{project},opencontainers}
ln -s $(dirs +1 -l) src/%{import_path}
popd

ln -s vendor src
export GOPATH=$(pwd)/_output:$(pwd)
export BUILDTAGS="selinux seccomp $(./hack/btrfs_tag.sh) $(./hack/libdm_tag.sh) containers_image_ostree_stub"
GOPATH=$GOPATH BUILDTAGS=$BUILDTAGS %gobuild -o bin/%{service_name} %{import_path}/cmd/%{service_name}
BUILDTAGS=$BUILDTAGS %{__make} bin/conmon bin/pause docs


%install
sed -i 's/\/local//' contrib/systemd/%{service_name}.service
./bin/%{service_name} \
      --selinux \
      --cgroup-manager "systemd" \
      --conmon "%{_libexecdir}/%{service_name}/conmon" \
      --cni-plugin-dir "%{_libexecdir}/cni" \
      --default-mounts "%{_datadir}/rhel/secrets:/run/secrets" \
      --file-locking=false config > %{service_name}.conf

%{__make} GOPATH=$(pwd)/_output:$(pwd) DESTDIR=%{buildroot} PREFIX=%{buildroot}%{_usr} install.config install.systemd install.completions

# install binaries
install -dp %{buildroot}{%{_bindir},%{_libexecdir}/%{service_name}}
install -p -m 755 bin/%{service_name} %{buildroot}%{_bindir}
install -p -m 755 bin/conmon %{buildroot}%{_libexecdir}/%{service_name}
install -p -m 755 bin/pause %{buildroot}%{_libexecdir}/%{service_name}

install -dp %{buildroot}%{_sysconfdir}/cni/net.d
install -p -m 644 contrib/cni/10-crio-bridge.conf %{buildroot}%{_sysconfdir}/cni/net.d/100-crio-bridge.conf
install -p -m 644 contrib/cni/99-loopback.conf %{buildroot}%{_sysconfdir}/cni/net.d/200-loopback.conf

install -dp %{buildroot}%{_sysconfdir}/sysconfig
install -p -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/%{service_name}-network
install -p -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/%{service_name}-storage

install -dp %{buildroot}%{_mandir}/man{1,5,8}
install -m 644 docs/*.5 %{buildroot}%{_mandir}/man5
install -m 644 docs/*.8 %{buildroot}%{_mandir}/man8

mkdir -p %{buildroot}%{_sharedstatedir}/containers

%check
%if 0%{?with_check}
export GOPATH=%{buildroot}/%{gopath}:$(pwd)/Godeps/_workspace:%{gopath}
%endif

%post
%systemd_post %{service_name}

%preun
%systemd_preun %{service_name}

%postun
%systemd_postun_with_restart %{service_name}

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files
%license LICENSE
%doc README.md
%{_bindir}/%{service_name}
%{_mandir}/man5/%{service_name}.conf.5*
%{_mandir}/man8/%{service_name}.8*
%dir %{_sysconfdir}/%{service_name}
%config(noreplace) %{_sysconfdir}/%{service_name}/%{service_name}.conf
%config(noreplace) %{_sysconfdir}/%{service_name}/seccomp.json
%config(noreplace) %{_sysconfdir}/sysconfig/%{service_name}-storage
%config(noreplace) %{_sysconfdir}/sysconfig/%{service_name}-network
%config(noreplace) %{_sysconfdir}/crictl.yaml
%dir %{_libexecdir}/%{service_name}
%{_libexecdir}/%{service_name}/conmon
%{_libexecdir}/%{service_name}/pause
%{_unitdir}/%{service_name}.service
%{_unitdir}/%{name}.service
%{_unitdir}/%{service_name}-shutdown.service
%dir %{_sharedstatedir}/containers
%dir %{_datadir}/oci-umount
%dir %{_datadir}/oci-umount/oci-umount.d
%{_datadir}/oci-umount/oci-umount.d/%{service_name}-umount.conf

%files cni-configs
%config(noreplace) %{_sysconfdir}/cni/net.d/100-%{service_name}-bridge.conf
%config(noreplace) %{_sysconfdir}/cni/net.d/200-loopback.conf


%changelog
* Wed Aug 11 2021 Peter Hunt <pehunt@redhat.com> - 1.11.16-0.16.rhaos3.11.git54f9e69
- rhbz#1958718: bump to 54f9e69

* Mon Aug 09 2021 Peter Hunt <pehunt@redhat.com> - 1.11.16-0.15.rhaos3.11.gitd7a399f
- bump to d7a399f2
- Resolves: rhbz#1965900

* Tue May 25 2021 Jindrich Novy <jnovy@redhat.com> - 1.11.16-0.14.rhaos3.11.git5218c73
- fix "ImageStatus request got "Manifest does not match provided manifest" when digest is not equal to the sha256 id in name under /var/lib/containers/storage/overlay-images/images.json"
- Resolves: #1955657

* Tue Oct 13 2020 Peter Hunt <pehunt@redhat.com> - 1.11.16-0.13.rhaos3.11.git5218c73
- bump to 5218c73
- Resolves: #1867463

* Wed Sep 02 2020 Peter Hunt <pehunt@redhat.com> - 1.11.16-0.12.rhaos3.11.git9c0200f
- bump to v1.11.16

* Mon Aug 10 2020 Peter Hunt <pehunt@redhat.com> - 1.11.16-0.11.dev.rhaos3.11.gitd6a416d
- Bump to d6a416d

* Wed Jun 17 2020 Peter Hunt <pehunt@redhat.com> - 1.11.16-0.10.dev.rhaos3.11.git1eee681
- bump to 1eee681

* Mon May 04 2020 Jindrich Novy <jnovy@redhat.com> - 1.11.16-0.9.dev.rhaos3.11.git6d43aae
- fix "[conmon] Liveness probes timeout unexpectedly"
- Resolves: #1774184

* Tue Feb 18 2020 Lokesh Mandvekar (Bot) <lsm5+bot@redhat.com> - 1.11.16-0.8.dev.rhaos3.11.git6d43aae
- autobuilt 6d43aae

* Wed Feb 12 2020 Jindrich Novy <jnovy@redhat.com> - 1.11.16-0.7.dev.rhaos3.11.git349831c
- Fix "crio[pid]: log: exiting because of error: write /tmp/crio.hostname.root.log.WARNING.timestamp.pid: no space left on device"
- Resolves: #1796066

* Mon Feb 10 2020 Lokesh Mandvekar (Bot) <lsm5+bot@redhat.com> - 1.11.16-0.6.dev.rhaos3.11.git349831c
- autobuilt 349831c

* Mon Jan 20 2020 Jindrich Novy <jnovy@redhat.com> - 1.11.16-0.5.dev.rhaos3.11.git3f89eba
- Fix thread safety of gpgme (#1792243)

* Thu Nov 21 2019 Jindrich Novy <jnovy@redhat.com> - 1.11.16-0.4.dev.rhaos3.11.git3f89eba
- move CNI configs to a separate subpackage
- Resolves: #1579445

* Tue Sep 17 2019 Jindrich Novy <jnovy@redhat.com> - 1.11.16-0.3.dev.rhaos3.11.git3f89eba
- Use autosetup macro again.
- Remove unused patches.

* Thu Sep 12 2019 Jindrich Novy <jnovy@redhat.com> - 1.11.16-0.2.dev.rhaos3.11.git3f89eba
- Fix CVE-2019-10214 (#1734646).

* Mon Aug 26 2019 Lokesh Mandvekar (Bot) <lsm5+bot@redhat.com> - 1.11.16-0.1.dev.rhaos3.11.git3f89eba
- bump to 1.11.16
- autobuilt 3f89eba

* Mon Jul 29 2019 Lokesh Mandvekar <lsm5@redhat.com> - 1.11.14-2.rhaos3.11.gitd56660e
- Resolves: #1730919

* Thu May 09 2019 Lokesh Mandvekar <lsm5@redhat.com> - 1.11.14-1.rhaos3.11.gitd56660e
- bump to v1.11.14

* Thu Apr 04 2019 Lokesh Mandvekar <lsm5@redhat.com> - 1.11.13-1.rhaos3.11.gitfb88a9c
- bump to v1.11.13

* Thu Apr 04 2019 Lokesh Mandvekar <lsm5@redhat.com> - 1.11.12-1.rhaos3.11.git846d94b
- bump to v1.11.12

* Wed Jan 16 2019 Lokesh Mandvekar <lsm5@redhat.com> - 1.11.11-1.rhaos3.11.git474f73d
- bump to v1.11.11

* Fri Nov 16 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.11.10-1.rhaos3.11.git42c86f0
- bump to v1.11.10

* Mon Nov 12 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.11.9-1.rhaos3.11.gitaa87e49
- bump to v1.11.9

* Thu Nov 08 2018 Frantisek Kluknavsky <fkluknav@redhat.com> - 1.11.8-2.rhaos3.11.git71cc465
- remove a weird dependency on  go-toolset-7-golang

* Fri Oct 26 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.11.8-1.rhaos3.11.git71cc465
- bump to v1.11.8
- built commit 71cc465

* Fri Oct 19 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.11.7-1.rhaos3.11.git17bfe63
- bump to v1.11.7
- built commit 17bfe63

* Fri Sep 28 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.11.6-1.rhaos3.11.git2d0f8c7
- bump to v1.11.6
- built commit 2d0f8c7

* Thu Sep 20 2018 Frantisek Kluknavsky <fkluknav@redhat.com> - 1.11.5-2.rhaos3.11.git1c8a4b1
- rebuilt

* Fri Sep 14 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.11.4-2.rhaos3.11.gite0c89d8
- update crio.conf default settings

* Fri Sep 14 2018 Lokesh Mandvekar <lsm5@redhat.com> - 1.11.4-1.rhaos3.11.gite0c89d8
- bump to v1.11.4
- epoch not needed for rhel

* Tue Sep 11 2018 Frantisek Kluknavsky <fkluknav@redhat.com> - 2:1.11.3-2.rhaos3.11.git4fbb022
- rebase

* Fri Aug 17 2018 Dan Walsh <dwalsh@redhat.com> - 2:1.11.2-1.rhaos3.11.git3eac3b2
- bump to v1.11.2

* Wed Jul 11 2018 Dan Walsh <dwalsh@redhat.com> - 2:1.11.1-2.rhaos3.11.git1759204
- Fix version of commit

* Tue Jul 10 2018 Dan Walsh <dwalsh@redhat.com> - 2:1.11.1-1.rhaos3.11.git76a48bd
- bump to v1.11.1

* Mon Jul 2 2018 Dan Walsh <dwalsh@redhat.com> - 2:1.11.0-1.rhaos3.11.git441bd3d
- bump to v1.11.0

* Mon Jul 2 2018 Dan Walsh <dwalsh@redhat.com> - 2:1.10.5-1.rhaos3.10.git
- bump to v1.10.5

* Wed Jun 27 2018 Lokesh Mandvekar <lsm5@redhat.com> - 2:1.10.4-1.rhaos3.10.gitebaa77a
- bump to v1.10.4
- remove devel and unittest subpackages - unused
- debuginfo disabled for now, complains about %%files being empty

* Mon Jun 18 2018 Dan Walsh <dwalsh@redhat.com> - 2:1.10.3-1.rhaos3.10.gite558bd
- bump to v1.10.3

* Tue Jun 12 2018 Dan Walsh <dwalsh@redhat.com> - 2:1.10.2-2.rhaos3.10.git1ffcbb
- Released version of v1.10.2

* Tue May 15 2018 Lokesh Mandvekar <lsm5@redhat.com> - 2:1.10.2-1.rhaos3.10.git095e88c
- bump to v1.10.2
- built commit 095e88c
- include rhaos3.10 in release tag
- do not compress debuginfo with dwz to support delve debugger

* Tue May 8 2018 Dan Walsh <dwalsh@redhat.com> - 2:1.10.1-2.git728df92
- bump to v1.10.1

* Wed Mar 28 2018 Lokesh Mandvekar <lsm5@redhat.com> - 2:1.10.0-1.beta.1gitc956614
- bump to v1.10.0-beta.1
- built commit c956614

* Tue Mar 13 2018 Dan Walsh <dwalsh@redhat.com> - 2:1.9.10-1.git8723732
- bump to v1.9.10

* Fri Mar 09 2018 Dan Walsh <dwalsh@redhat.com> - 2:1.9.9-1.git4d7e7dc
- bump to v1.9.9

* Fri Feb 23 2018 Lokesh Mandvekar <lsm5@redhat.com> - 2:1.9.8-1.git7d9d2aa
- bump to v1.9.8

* Fri Feb 23 2018 Lokesh Mandvekar <lsm5@redhat.com> - 2:1.9.7-2.gita98f9c9
- correct version in previous changelog entry

* Fri Feb 23 2018 Dan Walsh <dwalsh@redhat.com> - 2:1.9.7-1.gita98f9c9
- Merge pull request #1357 from runcom/netns-fixes
- sandbox_stop: close/remove the netns _after_ stopping the containers
- sandbox net: set netns closed after actaully closing it

* Wed Feb 21 2018 Dan Walsh <dwalsh@redhat.com> - 2:1.9.6-1.git5e48c92
- vendor: update c/image to handle text/plain from registries

* Fri Feb 16 2018 Dan Walsh <dwalsh@redhat.com> - 2:1.9.5-1.git125ec8a
- image: Add lock around image cache access

* Thu Feb 15 2018 Dan Walsh <dwalsh@redhat.com> - 2:1.9.4-1.git28c7dee
- imageService: cache information about images
- container_create: correctly set user
- system container: add /var/tmp as RW

* Sun Feb 11 2018 Dan Walsh <dwalsh@redhat.com> - 2:1.9.3-1.git63ea1dd
- Update containers/image and containers/storage
-   Pick up lots of fixes in image and storage library

* Thu Feb 8 2018 Dan Walsh <dwalsh@redhat.com> - 2:1.9.2-1.gitb066a83
- sandbox: fix sandbox logPath when crio restarts
- syscontainers, rhel: add ADDTL_MOUNTS
- Adapt to recent containers/image API updates
- container_create: only bind mount /etc/hosts if not provided by k8s

* Wed Jan 24 2018 Dan Walsh <dwalsh@redhat.com> - 2:1.9.1-1.gitb066a8
- Final Release 1.9.1

* Wed Jan 03 2018 Frantisek Kluknavsky <fkluknav@redhat.com> - 2:1.8.4-4.gitdffb5c2
- epoch not needed, 1.9 was never shipped, 1.8 with epoch also never shipped

* Wed Jan 03 2018 Frantisek Kluknavsky <fkluknav@redhat.com> - 2:1.8.4-3.gitdffb5c2
- reversed to 1.8, epoch

* Mon Dec 18 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.9.0-1.git814c6ab
- bump to v1.9.0

* Fri Dec 15 2017 Dan Walsh <dwalsh@redhat.com> - 1.8.4-1.gitdffb5c2
- bump to v1.8.4

* Wed Nov 29 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.8.2-1.git3de7ab4
- bump to v1.8.2

* Mon Nov 20 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.8.0-1.git80f54bc
- bump to v1.8.0

* Wed Nov 15 2017 Dan Walsh <dwalsh@redhat.com> - 1.0.4-2.git4aceedee
- Fix script error in kpod completions.

* Mon Nov 13 2017 Dan Walsh <dwalsh@redhat.com> - 1.0.4-1.git4aceedee
- bump to v1.0.4
- Add crictl.yaml
- Add prometheous end points
- Several bug fixes

* Fri Nov 10 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.3-1.git17bcfb4
- bump to v1.0.3

* Fri Nov 03 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.2-3.git748bc46
- enable debuginfo for C binaries

* Fri Nov 03 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.2-2.git748bc46
- enable debuginfo

* Mon Oct 30 2017 Dan Walsh <dwalsh@redhat.com> - 1.0.2-1.git748bc46
- Lots of bug fixes
- Fixes to pass cri-tools tests

* Wed Oct 25 2017 Dan Walsh <dwalsh@redhat.com> - 1.0.1-1.git64a30e1
- Lots of bug fixes
- Fixes to pass cri-tools tests

* Thu Oct 19 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-7.gita636972
- update dep NVRs
- update release tag

* Mon Oct 16 2017 Dan Walsh <dwalsh@redhat.com> - 1.0.0-6.gita636972
- Get the correct checksum
- Setup storage-opt to override kernel check

* Fri Oct 13 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-2.gitcd1bac5
- bump to v1.0.0
- require containernetworking-plugins >= 0.5.2-3

* Wed Oct 11 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-1.rc3.gitd2c6f64
- bump to v1.0.0-rc3

* Wed Sep 20 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-1.rc2.git6784a66
- bump to v1.0.0-rc2

* Mon Sep 18 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-2.rc1.gitbb1da97
- bump release tag and build for extras

* Mon Sep 18 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-1.rc1.gitbb1da97
- bump to v1.0.0-rc1 tag
- built commit bb1da97
- use bundled deps
- disable devel package
- remove redundant meta-provides

* Thu Aug 3 2017 Dan Walsh <dwalsh@redhat.com> - 1.0.0.beta.0-1.git66d96e7
- Beta Release
-   Additional registry support
-   Daemon pids-limit support
-   cri-o daemon now supports a default pid-limit on all containers to prevent fork-bombs. This is configurable by admins through a flag or /etc/crio/crio.conf
-   Configurable image volume support
-   Bugs and Stability fixes
-   OCI 1.0 runtime support
-     Dropped internal runc, and now use systems runc 

* Fri Jun 30 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.0.0.alpha.0-1.git91977d3
- built commit 91977d3
- remove cri-o-cni subpackage
- require containernetworking-plugins >= 0.5.2-2 (same as containernetworking-cni)

* Fri Jun 23 2017 Antonio Murdaca <runcom@fedoraproject.org> - 1.0.0.alpha.0-0.git5dcbdc0.3
- rebuilt to include cri-o-cni sub package

* Wed Jun 21 2017 Antonio Murdaca <runcom@fedoraproject.org> - 1.0.0.alpha.0-0.git5dcbdc0.2
- rebuilt for s390x

* Wed Jun 21 2017 Antonio Murdaca <runcom@fedoraproject.org> - 1.0.0.alpha.0-0.git5dcbdc0.1
- built first alpha release

* Fri May 5 2017 Dan Walsh <dwalsh@redhat.com> 0.3-0.gitf648cd6e
- Bump up version to 0.3

* Tue Mar 21 2017 Dan Walsh <dwalsh@redhat.com> 0.2-1.git7d7570e
- Bump up version to 0.2

* Tue Mar 21 2017 Dan Walsh <dwalsh@redhat.com> 0.1-1.git9bf26b5
- Bump up version to 0.1

* Mon Feb 13 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0-0.15.git0639f06
- built commit 0639f06
- packaging workarounds for 'go install'

* Wed Feb 8 2017 Dan Walsh <dwalsh@redhat.com> 0-0.14.git6bd7c53
- Use newer versions of runc
- Applying k8s kubelet v3 api to cri-o server
- Applying k8s.io v3 API for ocic and ocid
- doc: Add instruction to run cri-o with kubernetes
- Lots of  updates of container/storage and containers/image

* Mon Jan 23 2017 Peter Robinson <pbrobinson@fedoraproject.org> 0-0.13.git7cc8492
- Build on all kubernetes arches

* Fri Jan 20 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0-0.12.git7cc8492
- add bash completion
- From: Daniel J Walsh <dwalsh@redhat.com>

* Thu Jan 19 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0-0.11.git7cc8492
- remove trailing whitespace from unitfile

* Thu Jan 19 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0-0.10.git7cc8492
- built commit 7cc8492
- packaging fixes from Nalin Dahyabhai <nalin@redhat.com>

* Thu Jan 19 2017 Dan Walsh <dwalsh@redhat.com> - 0-0.9.gitb9dc097
- Change to require skopeo-containers
- Merge Nalind/storage patch
-    Now uses Storage for Image Management

* Mon Jan 16 2017 Lokesh Manvekar <lsm5@fedoraproject.org> - 0-0.8.git2e6070f
- packaging changes from Nalin Dahyabhai <nalin@redhat.com>
- Don't make the ExecReload setting part of the ExecStart setting.
- Create ocid.conf in install, not in check.
- Own /etc/ocid.
- Install an "anything goes" pulling policy for a default.

* Thu Dec 22 2016 Dan Walsh <dwalsh@redhat.com> - 0-0.7.git2e6070f
- Switch locate to /var/lib/containers for images

* Thu Dec 22 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0-0.6.git2e6070f
- built commit 2e6070f

* Wed Dec 21 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0-0.5.git36dfef5
- install plugins into /usr/libexec/ocid/cni/
- require runc >= 1.0.0 rc2

* Wed Dec 21 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0-0.4.git36dfef5
- built runcom/alpha commit 36dfef5
- cni bundled for now

* Thu Dec 15 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0-0.3.gitc57530e
- Resolves: #1392977 - first upload to Fedora
- add build deps, enable only for x86_64 (doesn't build on i686)

* Thu Dec 15 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0-0.2.gitc57530e
- add Godeps.json

* Tue Nov 08 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0-0.1.gitc57530e
- First package for Fedora


