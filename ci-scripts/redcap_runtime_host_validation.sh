#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/..")
SCENARIO=${1:-container_5g_flexric_rfsim_redcap.xml}
TIMESTAMP=$(date +%F_%H-%M-%S)
RUN_LOG="${REPO_ROOT}/test_log/compiler_logs/redcap_runtime_host_${TIMESTAMP}.log"
SUMMARY_MD="${REPO_ROOT}/test_log/report/redcap_runtime_host_summary_${TIMESTAMP}.md"

mkdir -p "${REPO_ROOT}/test_log/compiler_logs" "${REPO_ROOT}/test_log/report"

cd "${SCRIPT_DIR}"

set +e
./run_locally.sh "${SCENARIO}" 2>&1 | tee "${RUN_LOG}"
RUN_RC=${PIPESTATUS[0]}
set -e

python3 "${SCRIPT_DIR}/redcap_runtime_summary.py" \
  --scenario "${SCENARIO}" \
  --run-log "${RUN_LOG}" \
  --output "${SUMMARY_MD}"

echo "[Run Log] ${RUN_LOG}"
echo "[Summary] ${SUMMARY_MD}"

exit "${RUN_RC}"
