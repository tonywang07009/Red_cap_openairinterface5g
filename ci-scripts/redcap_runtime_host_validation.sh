#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/..")
SCENARIO=${1:-container_5g_flexric_rfsim_redcap.xml}
TIMESTAMP=$(date +%F_%H-%M-%S)
EXPECTED_MODE=${REDCAP_EXPECTED_MODE:-}
GNB_CONFIG_PATH=${REDCAP_GNB_CONFIG_PATH:-}
COMPOSE_ENV_FILE="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/.env"
FILE_SUFFIX=${EXPECTED_MODE:+_${EXPECTED_MODE}}
RUN_LOG="${REPO_ROOT}/test_log/compiler_logs/redcap_runtime_host${FILE_SUFFIX}_${TIMESTAMP}.log"
SUMMARY_MD="${REPO_ROOT}/test_log/report/redcap_runtime_host_summary${FILE_SUFFIX}_${TIMESTAMP}.md"

mkdir -p "${REPO_ROOT}/test_log/compiler_logs" "${REPO_ROOT}/test_log/report"

cd "${SCRIPT_DIR}"

cleanup() {
  if [ -n "${GNB_CONFIG_PATH}" ]; then
    rm -f "${COMPOSE_ENV_FILE}"
  fi
}

trap cleanup EXIT

if [ -n "${GNB_CONFIG_PATH}" ]; then
  printf 'GNB_REDCAP_CONFIG="%s"\n' "${GNB_CONFIG_PATH}" > "${COMPOSE_ENV_FILE}"
fi

set +e
./run_locally.sh "${SCENARIO}" 2>&1 | tee "${RUN_LOG}"
RUN_RC=${PIPESTATUS[0]}
set -e

summary_args=(
  --scenario "${SCENARIO}"
  --run-log "${RUN_LOG}"
  --output "${SUMMARY_MD}"
)

if [ -n "${EXPECTED_MODE}" ]; then
  summary_args+=(--expected-mode "${EXPECTED_MODE}")
fi

if [ -n "${GNB_CONFIG_PATH}" ]; then
  summary_args+=(--config "${GNB_CONFIG_PATH}")
fi

python3 "${SCRIPT_DIR}/redcap_runtime_summary.py" "${summary_args[@]}"

echo "[Run Log] ${RUN_LOG}"
echo "[Summary] ${SUMMARY_MD}"

exit "${RUN_RC}"
