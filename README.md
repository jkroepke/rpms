[![Copr build status](https://copr.fedorainfracloud.org/coprs/jkroepke/git/package/git/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/jkroepke/git/package/git/)

# rpm-git
Provides latest git for enterprise linux

It's periodically scrape the git source rpm from fedora rawhide and compiles it for RHEL 7 and RHEL 8.

## Build infrastructure

I'm using fedora corp to build, provide and distriubte the rpms.

https://copr.fedorainfracloud.org/coprs/jkroepke/git/package/git/

### yum.repo file

EL7: https://copr.fedorainfracloud.org/coprs/jkroepke/git/repo/epel-7/jkroepke-git-epel-7.repo

EL8: https://copr.fedorainfracloud.org/coprs/jkroepke/git/repo/epel-8/jkroepke-git-epel-8.repo
