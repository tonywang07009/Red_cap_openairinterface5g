#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/..")
SCENARIO=${1:-container_5g_flexric_rfsim_redcap.xml}
TIMESTAMP=$(date +%F_%H-%M-%S)
MATRIX_LOG="${REPO_ROOT}/test_log/compiler_logs/redcap_runtime_matrix_${TIMESTAMP}.log"

mkdir -p "${REPO_ROOT}/test_log/compiler_logs" "${REPO_ROOT}/test_log/runtime_configs"
overall_rc=0

run_case() {
  local mode="$1"
  local config_path="${REPO_ROOT}/test_log/runtime_configs/gnb.redcap.${mode}.${TIMESTAMP}.yaml"
  local case_rc=0

  python3 "${SCRIPT_DIR}/redcap_prepare_runtime_config.py" \
    --mode "${mode}" \
    --output "${config_path}"

  echo "===== ${mode} =====" | tee -a "${MATRIX_LOG}"
  set +e
  REDCAP_EXPECTED_MODE="${mode}" \
  REDCAP_GNB_CONFIG_PATH="${config_path}" \
    "${SCRIPT_DIR}/redcap_runtime_host_validation.sh" "${SCENARIO}" 2>&1 | tee -a "${MATRIX_LOG}"
  case_rc=${PIPESTATUS[0]}
  set -e

  if [ ${case_rc} -ne 0 ]; then
    overall_rc=${case_rc}
  fi
}

run_case case-a
run_case case-b

echo "[Matrix Log] ${MATRIX_LOG}"
exit "${overall_rc}"
