#!/bin/bash

set -euo pipefail

exec docker run --rm -ti fedora:rawhide bash -c "yum info git | grep Source | awk '{ print \$3 }' | tr -d '[:space:]'"