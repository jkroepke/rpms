#!/bin/bash

set -euo pipefail

curl -sSfL http://ftp.redhat.com/redhat/linux/enterprise/7Server/en/RHOSE/SRPMS/ | grep golang-github-cpuguy83-go-md2man-1.0.7 | tail -1 | sed -E 's/.*href="([^"]*)".*/\1/'
