#!/bin/bash

set -euo pipefail

exec docker run --rm fedora:rawhide \
  bash -c "yum info git | grep Source | awk '{ print \$3 }' | tr -d '[:space:]' | grep -v rc"
