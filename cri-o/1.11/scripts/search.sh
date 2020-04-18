#!/bin/bash

set -euo pipefail

curl -sSfL http://ftp.redhat.com/redhat/linux/enterprise/7Server/en/RHOSE/SRPMS/ | grep cri-o-1.11 | tail -1 | sed -E 's/.*href="([^"]*)".*/\1/'
