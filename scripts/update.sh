#!/bin/bash

set -euo pipefail

VERSION=${1:-"$(./scripts/search.sh)"}

rm -rf packages/*

curl -sSf -LJ \
  -o ./tmp/git.src.rpm \
  "https://download.fedoraproject.org/pub/fedora/linux/development/rawhide/Everything/source/tree/Packages/g/${VERSION}"

docker run --rm -ti \
  --name unpack-rpm \
  -v "${PWD}:/work" \
  -w /work/packages/ \
  centos:8 \
  bash -c "rpm2cpio /work/tmp/git.src.rpm | cpio -idmv --no-absolute-filenames"

rm -rf packages/git*.tar.*

if [ -z "${CI+x}" ]; then
  git add -A
  git commit -m "Update to ${VERSION}"
  git push
fi
