#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/..")

REBUILD_RAN_BASE=${REDCAP_REBUILD_RAN_BASE:-0}
NO_CACHE=${REDCAP_DOCKER_NO_CACHE:-0}
BUILD_OPTION=${REDCAP_BUILD_OPTION:-}

docker_build_args=()
if [ "${NO_CACHE}" = "1" ]; then
  docker_build_args+=(--no-cache)
fi

build_image() {
  local tag="$1"
  local dockerfile="$2"
  shift 2
  local extra_args=("$@")

  echo "[Build] ${tag} <- ${dockerfile}"
  docker build "${docker_build_args[@]}" \
    "${extra_args[@]}" \
    --tag "${tag}" \
    --file "${dockerfile}" \
    "${REPO_ROOT}"
  echo
}

if [ "${REBUILD_RAN_BASE}" = "1" ] || ! docker image inspect ran-base:latest >/dev/null 2>&1; then
  build_image "ran-base:latest" "${REPO_ROOT}/docker/Dockerfile.base.ubuntu" --target ran-base
else
  echo "[Skip] ran-base:latest already exists"
  echo
fi

build_args=()
if [ -n "${BUILD_OPTION}" ]; then
  build_args+=(--build-arg "BUILD_OPTION=${BUILD_OPTION}")
fi

build_image "ran-build:latest" "${REPO_ROOT}/docker/Dockerfile.build.ubuntu" --target ran-build "${build_args[@]}"
build_image "oai-gnb:latest" "${REPO_ROOT}/docker/Dockerfile.gNB.ubuntu" "${build_args[@]}"
build_image "oai-nr-ue:latest" "${REPO_ROOT}/docker/Dockerfile.nrUE.ubuntu" "${build_args[@]}"

echo "[Done] Local RedCap runtime images rebuilt from workspace"
echo "[Next] Verify binary markers with: bash redcap_interface/redcap_inspect_gnb_image.sh"
