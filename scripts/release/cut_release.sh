#!/bin/bash
set -euo pipefail

function make_release_id {
    SEQ_FORMATTED=$(printf "%02d" "${SEQ?}")
    echo "${DATE?}_${SEQ_FORMATTED?}_RC00"
}

# Build up a release name based on the current data.
DATE=$(date "+%Y-%m-%d")
SEQ=0

RELEASE_ID=$(make_release_id)
while git tag | grep -q "${RELEASE_ID?}"; do
    SEQ=$(( SEQ + 1 ))
    RELEASE_ID=$(make_release_id)
done

echo "Next release ID: ${RELEASE_ID?}"
git tag "${RELEASE_ID?}"
git push origin --tags
