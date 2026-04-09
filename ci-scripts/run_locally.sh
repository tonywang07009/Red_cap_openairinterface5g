#!/bin/bash

set -euo pipefail
SHORT_COMMIT_SHA=$(git rev-parse --short=8 HEAD)
COMMIT_SHA=$(git rev-parse HEAD)
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
REPO_PATH=$(dirname $(realpath $0))/../
TESTCASE_INPUT=${1:-}

if [ $# -eq 0 ]
  then
    echo "Provide a testcase as an argument"
    exit 1
fi

TESTCASE=${TESTCASE_INPUT#xml_files/}

if [ ! -f "xml_files/${TESTCASE}" ]; then
    echo "Cannot find scenario xml_files/${TESTCASE}" >&2
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "Docker access is required to run CI scenarios locally" >&2
    exit 1
fi

if ! python3 -c 'import yaml, paramiko' >/dev/null 2>&1; then
    echo "Missing Python dependencies. Run: python3 -m pip install -r ci-scripts/requirements.txt" >&2
    exit 1
fi

need_image() {
    local image="$1"
    if ! docker image inspect "${image}" >/dev/null 2>&1; then
        echo "Required local image missing: ${image}" >&2
        exit 1
    fi
}

tag_if_present() {
    local image="$1"
    local tag="$2"
    if docker image inspect "${image}" >/dev/null 2>&1; then
        docker tag "${image}" "${tag}"
    else
        echo "Skipping optional image tag for ${image}" >&2
    fi
}

# The script assumes you've build the following images:
#
# docker build . -f docker/Dockerfile.gNB.ubuntu -t oai-gnb
# docker build . -f docker/Dockerfile.nr-cuup.ubuntu -t oai-nr-cuup
# docker build . -f docker/Dockerfile.nrUE.ubuntu -t oai-nr-ue
#
# The images above depend on the following images:
#
# docker build . -f docker/Dockerfile.build.ubuntu -t ran-build
# docker build . -f docker/Dockerfile.base.ubuntu -t ran-base

need_image oai-nr-ue
need_image oai-gnb

docker tag oai-nr-ue oai-ci/oai-nr-ue:develop-${SHORT_COMMIT_SHA}
docker tag oai-gnb oai-ci/oai-gnb:develop-${SHORT_COMMIT_SHA}
tag_if_present oai-nr-cuup oai-ci/oai-nr-cuup:develop-${SHORT_COMMIT_SHA}

python3 main.py --mode=InitiateHtml --ranRepository=NONE --ranBranch=${CURRENT_BRANCH} \
    --ranCommitID=${COMMIT_SHA} --ranAllowMerge=false \
    --ranTargetBranch=NONE \
    --XMLTestFile=xml_files/${TESTCASE} --local

python3 main.py --mode=TesteNB --ranRepository=NONE --ranBranch=${CURRENT_BRANCH} \
    --ranCommitID=${COMMIT_SHA} --ranAllowMerge=false \
    --ranTargetBranch=NONE \
    --eNBSourceCodePath=${REPO_PATH} \
    --XMLTestFile=xml_files/${TESTCASE} --local
RET=$?

python3 main.py --mode=FinalizeHtml --local

exit ${RET}
