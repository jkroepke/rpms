#!/bin/bash

set -euo pipefail

VERSION=${1:-"$(./scripts/search.sh)"}

if [ "${VERSION}" != "" ]; then
  rm -rf packages/*

  curl -sSf -LJ \
    -o ./tmp/src.rpm \
    "https://download.fedoraproject.org/pub/fedora/linux/development/rawhide/Everything/source/tree/Packages/g/${VERSION}"

  docker run --rm \
    --name unpack-rpm \
    -v "${PWD}:/work" \
    -w /work/packages/ \
    centos:8 \
    bash -c "rpm2cpio /work/tmp/src.rpm | cpio -idmv --no-absolute-filenames"

  if [ -n "${GITHUB_EVENT_PATH+x}" ]; then
    if ! git diff --exit-code; then
      git add -A
      git config --global user.name 'Jan-Otto Kröpke'
      git config --global user.email 'jkroepke@users.noreply.github.com'
      git commit -m "Update to ${VERSION}"
    fi
  fi
else
  exit 0
fi
