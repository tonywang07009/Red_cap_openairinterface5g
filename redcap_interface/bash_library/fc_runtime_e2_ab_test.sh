#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
INTERFACE_DIR=$(realpath "${SCRIPT_DIR}/..")
REPO_ROOT=$(realpath "${INTERFACE_DIR}/..")
SCENARIO=${1:-container_5g_flexric_rfsim_redcap.xml}
TIMESTAMP=$(date +%F_%H-%M-%S)
AB_LOG="${REPO_ROOT}/test_log/compiler_logs/redcap_runtime_e2_ab_${TIMESTAMP}.log"
overall_rc=0

mkdir -p "${REPO_ROOT}/test_log/compiler_logs"

run_case() {
  local e2_mode="$1"
  local case_rc=0

  echo "===== e2-agent=${e2_mode} =====" | tee -a "${AB_LOG}"
  set +e
  REDCAP_E2_AGENT_MODE="${e2_mode}" \
    "${SCRIPT_DIR}/fc_runtime_host_validation.sh" "${SCENARIO}" 2>&1 | tee -a "${AB_LOG}"
  case_rc=${PIPESTATUS[0]}
  set -e

  if [ ${case_rc} -ne 0 ] && [ ${overall_rc} -eq 0 ]; then
    overall_rc=${case_rc}
  fi
}

run_case enabled
run_case disabled

if [ "${REDCAP_INCLUDE_EMPTY_SM_DIR:-0}" = "1" ]; then
  run_case empty-sm-dir
fi

echo "[A/B Log] ${AB_LOG}"
exit "${overall_rc}"
