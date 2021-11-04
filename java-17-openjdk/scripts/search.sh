#!/bin/bash

set -euo pipefail

exec docker run --rm quay.io/centos/centos:stream8 \
  bash -c "yum info java-17-openjdk | grep Source | awk '{ print \$3 }' | tr -d '[:space:]' | sed '/\.rc/d'"
