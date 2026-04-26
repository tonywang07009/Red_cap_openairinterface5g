#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/..")
LIVE_PATTERN='RedCap UL PRB control RNTI [0-9A-Fa-f]{4} requested [0-9]+ effective [0-9]+'

# Prefer the direct gNB runtime marker when it is already flushed into docker logs.
if timeout 10 bash -lc "until docker logs rfsim5g-oai-gnb_redcap 2>&1 | grep -qE '${LIVE_PATTERN}'; do sleep 0.5; done"; then
  echo "Verified RedCap UL PRB control marker in live gNB logs"
  exit 0
fi

# Fallback: the control helper logs a positive ACK only after a successful RC control response.
latest_ctrl_log=$(ls -1t "${REPO_ROOT}/test_log/compiler_logs"/redcap_rc_ctrl_xapp_*.log 2>/dev/null | head -n 1 || true)
if [[ -n "${latest_ctrl_log}" ]] && grep -q "RedCap RC control sent node=" "${latest_ctrl_log}"; then
  echo "Verified RedCap UL PRB control via xApp ACK log: ${latest_ctrl_log}"
  exit 0
fi

echo "RedCap UL PRB control verification failed (no live gNB marker and no xApp ACK log)" >&2
exit 1
