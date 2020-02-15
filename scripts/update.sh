#!/bin/bash

rm -rf packages/*

curl -sSf -LJ \
  -o ./tmp/git.src.rpm \
  https://download.fedoraproject.org/pub/fedora/linux/development/rawhide/Everything/source/tree/Packages/g/git-2.25.0-1.fc32.src.rpm

docker run --rm -ti \
  --name unpack-rpm \
  -v "${PWD}:/work" \
  -w /work/packages/ \
  centos:8 \
  bash -c "rpm2cpio /work/tmp/git.src.rpm | cpio -idmv --no-absolute-filenames"

rm -rf git*.tar.*
