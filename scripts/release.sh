#!/usr/bin/env bash
set -e

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <version> <summary>"
  echo "Example: $0 v0.1.2 'Add AI builder improvements'"
  exit 1
fi

VERSION="$1"
SUMMARY="$2"

cat <<EOF
Release helper
==============

1. Update CHANGELOG.md under the Unreleased section with a new entry for ${VERSION}.
2. Run this script after committing the feature.

Commands:
  git tag -a ${VERSION} -m "${VERSION}: ${SUMMARY}"
  git push origin main
  git push origin ${VERSION}
EOF
