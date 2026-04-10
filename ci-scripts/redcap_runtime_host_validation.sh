#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/..")
SCENARIO=${1:-container_5g_flexric_rfsim_redcap.xml}
TIMESTAMP=$(date +%F_%H-%M-%S)
EXPECTED_MODE=${REDCAP_EXPECTED_MODE:-}
GNB_CONFIG_PATH=${REDCAP_GNB_CONFIG_PATH:-}
UE1_CONFIG_PATH=${NRUE_CONFIG_1_PATH:-${REDCAP_NRUE1_CONFIG_PATH:-}}
UE2_CONFIG_PATH=${NRUE_CONFIG_2_PATH:-${REDCAP_NRUE2_CONFIG_PATH:-}}
COMPOSE_ENV_FILE="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/.env"
FILE_SUFFIX=${EXPECTED_MODE:+_${EXPECTED_MODE}}
RUN_LOG="${REPO_ROOT}/test_log/compiler_logs/redcap_runtime_host${FILE_SUFFIX}_${TIMESTAMP}.log"
SUMMARY_MD="${REPO_ROOT}/test_log/report/redcap_runtime_host_summary${FILE_SUFFIX}_${TIMESTAMP}.md"
DEBUG_PREFIX="${REPO_ROOT}/test_log/compiler_logs/redcap_runtime_debug${FILE_SUFFIX}_${TIMESTAMP}"
COMPOSE_ENV_WRITTEN=0

mkdir -p "${REPO_ROOT}/test_log/compiler_logs" "${REPO_ROOT}/test_log/report"

cd "${SCRIPT_DIR}"

cleanup() {
  if [ "${COMPOSE_ENV_WRITTEN}" -eq 1 ]; then
    rm -f "${COMPOSE_ENV_FILE}"
  fi
}

trap cleanup EXIT

capture_debug_logs() {
  local container_name="$1"
  local output_file="$2"

  {
    echo "# container=${container_name}"
    echo "# collected_at=$(date --iso-8601=seconds)"
    docker logs "${container_name}" 2>&1 || echo "[WARN] unable to collect docker logs for ${container_name}"
  } > "${output_file}"
}

compose_env_lines=()

if [ -n "${GNB_CONFIG_PATH}" ]; then
  compose_env_lines+=("GNB_REDCAP_CONFIG=\"${GNB_CONFIG_PATH}\"")
fi

if [ -n "${UE1_CONFIG_PATH}" ]; then
  compose_env_lines+=("NRUE_CONFIG_1=\"${UE1_CONFIG_PATH}\"")
fi

if [ -n "${UE2_CONFIG_PATH}" ]; then
  compose_env_lines+=("NRUE_CONFIG_2=\"${UE2_CONFIG_PATH}\"")
fi

if [ "${#compose_env_lines[@]}" -gt 0 ]; then
  printf '%s\n' "${compose_env_lines[@]}" > "${COMPOSE_ENV_FILE}"
  COMPOSE_ENV_WRITTEN=1
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

if [ "${RUN_RC}" -ne 0 ]; then
  docker ps -a > "${DEBUG_PREFIX}_docker_ps_a.log" 2>&1 || true
  capture_debug_logs "rfsim5g-oai-gnb_redcap" "${DEBUG_PREFIX}_gnb.log"
  capture_debug_logs "rfsim5g-oai-nr-ue1_redcap" "${DEBUG_PREFIX}_ue1.log"
  capture_debug_logs "rfsim5g-oai-nr-ue2_redcap" "${DEBUG_PREFIX}_ue2.log"
  capture_debug_logs "nearRT-RIC_redcap" "${DEBUG_PREFIX}_nearRT-RIC.log"
fi

echo "[Run Log] ${RUN_LOG}"
echo "[Summary] ${SUMMARY_MD}"

exit "${RUN_RC}"
