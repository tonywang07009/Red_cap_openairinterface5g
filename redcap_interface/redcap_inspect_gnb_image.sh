#!/bin/bash

set -euo pipefail

IMAGE=${1:-oai-gnb:latest}
SHELL_BIN=${SHELL_BIN:-/bin/sh}

echo "[Image] ${IMAGE}"
echo "[Shell] ${SHELL_BIN}"
echo

echo "[Check] /usr/local/lib/flexric"
docker run --rm --entrypoint "${SHELL_BIN}" "${IMAGE}" -lc 'ls -l /usr/local/lib/flexric'
echo

echo "[Check] ldd /opt/oai-gnb/bin/nr-softmodem"
docker run --rm --entrypoint "${SHELL_BIN}" "${IMAGE}" -lc 'ldd /opt/oai-gnb/bin/nr-softmodem'
echo

echo "[Check] binary marker for BWP-fit PUCCH budget fix"
docker run --rm --entrypoint "${SHELL_BIN}" "${IMAGE}" -lc "grep -aF 'Reducing PUCCH reservation budget' /opt/oai-gnb/bin/nr-softmodem || true"
echo

echo "[Check] binary marker for legacy PUCCH assert"
docker run --rm --entrypoint "${SHELL_BIN}" "${IMAGE}" -lc "grep -aF 'Cannot allocate all required PUCCH resources for max number of' /opt/oai-gnb/bin/nr-softmodem || true"
