#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
INTERFACE_DIR=$(realpath "${SCRIPT_DIR}/..")
REPO_ROOT=$(realpath "${INTERFACE_DIR}/..")
LIVE_PATTERN='RedCap UL PRB control RNTI [0-9A-Fa-f]{4} requested [0-9]+ effective [0-9]+'

# Prefer the direct gNB runtime marker when it is already flushed into docker logs.
if timeout 10 bash -lc "until docker logs rfsim5g-oai-gnb_redcap 2>&1 | grep -qE '${LIVE_PATTERN}'; do sleep 0.5; done"; then
  echo "Verified RedCap UL PRB control marker in live gNB logs"
  exit 0
fi

# Large full64 docker logs can exceed the short live grep window. Fall back to
# the latest captured post-control gNB log before reporting a missing marker.
latest_gnb_log=$(ls -1t "${REPO_ROOT}/test_log/compiler_logs"/redcap_rc_ctrl_xapp_*_gnb_live_postcontrol.log 2>/dev/null | head -n 1 || true)
if [[ -n "${latest_gnb_log}" ]] && grep -qE "${LIVE_PATTERN}" "${latest_gnb_log}"; then
  echo "Verified RedCap UL PRB control marker in captured gNB log: ${latest_gnb_log}"
  exit 0
fi

# xApp ACK is useful path evidence, but G4 closes only on the gNB apply marker.
latest_ctrl_log=$(ls -1t "${REPO_ROOT}/test_log/compiler_logs"/redcap_rc_ctrl_xapp_*.log 2>/dev/null | head -n 1 || true)
if [[ -n "${latest_ctrl_log}" ]] && grep -q "RedCap RC control sent node=" "${latest_ctrl_log}"; then
  echo "Found xApp ACK log but no live gNB marker yet: ${latest_ctrl_log}" >&2
  exit 1
fi

echo "RedCap UL PRB control verification failed (no live gNB marker and no xApp ACK log)" >&2
exit 1
