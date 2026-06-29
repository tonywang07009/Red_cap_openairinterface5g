#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${PROJECT_DIR}/../../../.." && pwd)"
source "${SCRIPT_DIR}/redcap_runtime_common.sh"

COMPOSE_DIR="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap"
CONFIG_FILE="${PROJECT_DIR}/configs/BWP_local_matrix.yaml"
RUN_MODE="${1:---dry-run}"
RUN_ID="${RUN_ID:-$(date +%Y%m%d_%H%M%S)}"
LOG_DIR="${REPO_ROOT}/test_log/redcap_bwp_sdt_validation/${RUN_ID}_bwp"
SERVICES="${SERVICES:-nearRT-RIC oai-gnb oai-nr-ue2 xapp-kpm-rc}"
RUN_WAIT_SECONDS="${RUN_WAIT_SECONDS:-35}"
STOP_AFTER_RUN="${STOP_AFTER_RUN:-0}"
RUNTIME_SCENARIO="${RUNTIME_SCENARIO:-}"
BWP_TRIGGER_SEQUENCE="${BWP_TRIGGER_SEQUENCE:-}"
BWP_TRIGGER_DELAY_SECONDS="${BWP_TRIGGER_DELAY_SECONDS:-5}"
TRIGGER_FAILURES=0
RUNTIME_FAILURES=0

redcap_validate_run_mode "${RUN_MODE}"

mkdir -p "${LOG_DIR}"

redcap_export_local_image_defaults
redcap_export_rf_defaults
export MMTC_DRX_PROFILE="${MMTC_DRX_PROFILE:-balanced}"
export MMTC_BWP_INACTIVITY_TIMER_MS="${MMTC_BWP_INACTIVITY_TIMER_MS:-8}"
export MMTC_BWP_SWITCH_DELAY_MS="${MMTC_BWP_SWITCH_DELAY_MS:-1}"
export MMTC_BWP_TRAFFIC_PROFILE="${MMTC_BWP_TRAFFIC_PROFILE:-low_load}"
export MMTC_GNB_EXTRA_OPTIONS="${MMTC_GNB_EXTRA_OPTIONS:-} --telnetsrv --telnetsrv.shrmod ci --telnetsrv.listenaddr 127.0.0.1 --telnetsrv.listenport 9091"
if [[ -z "${RUNTIME_SCENARIO}" ]]; then
  RUNTIME_SCENARIO="${MMTC_BWP_TRAFFIC_PROFILE}_bwp_${MMTC_BWP_INACTIVITY_TIMER_MS}ms_${MMTC_BWP_SWITCH_DELAY_MS}ms"
fi

cat > "${LOG_DIR}/run_manifest.txt" <<EOF
experiment=BWP_switching_with_DRX
config=${CONFIG_FILE}
compose_root=${COMPOSE_DIR}
run_mode=${RUN_MODE}
services=${SERVICES}
REGISTRY=${REGISTRY}
GNB_IMG=${GNB_IMG}
NRUE_IMG=${NRUE_IMG}
TAG=${TAG}
run_wait_seconds=${RUN_WAIT_SECONDS}
stop_after_run=${STOP_AFTER_RUN}
runtime_scenario=${RUNTIME_SCENARIO}
MMTC_REDCAP_ENABLE=${MMTC_REDCAP_ENABLE}
MMTC_REDCAP_NUM_RX=${MMTC_REDCAP_NUM_RX}
MMTC_REDCAP_HALF_DUPLEX=${MMTC_REDCAP_HALF_DUPLEX}
MMTC_N_RB_DL=${MMTC_N_RB_DL}
MMTC_NUMEROLOGY=${MMTC_NUMEROLOGY}
MMTC_RF_FREQ=${MMTC_RF_FREQ}
MMTC_SSB_START=${MMTC_SSB_START}
MMTC_DRX_PROFILE=${MMTC_DRX_PROFILE}
MMTC_BWP_INACTIVITY_TIMER_MS=${MMTC_BWP_INACTIVITY_TIMER_MS}
MMTC_BWP_SWITCH_DELAY_MS=${MMTC_BWP_SWITCH_DELAY_MS}
MMTC_BWP_TRAFFIC_PROFILE=${MMTC_BWP_TRAFFIC_PROFILE}
BWP_TRIGGER_SEQUENCE=${BWP_TRIGGER_SEQUENCE}
BWP_TRIGGER_DELAY_SECONDS=${BWP_TRIGGER_DELAY_SECONDS}
MMTC_GNB_EXTRA_OPTIONS=${MMTC_GNB_EXTRA_OPTIONS}
note=BWP timer and switch-delay labels are recorded for scenario traceability; local bwp-InactivityTimer remains an implementation gap.
EOF

echo "[BWP] manifest: ${LOG_DIR}/run_manifest.txt"
echo "[BWP] config: ${CONFIG_FILE}"
echo "[BWP] services: ${SERVICES}"

if [[ "${RUN_MODE}" == "--dry-run" ]]; then
  echo "[BWP] dry-run only. Use --run to start docker compose through redcap_runtime_common.sh."
  exit 0
fi

read -r -a SERVICE_ARGS <<< "${SERVICES}"
redcap_compose_up "${COMPOSE_DIR}" "${SERVICE_ARGS[@]}" 2>&1 | tee "${LOG_DIR}/docker_compose_up.log"
redcap_compose_ps "${COMPOSE_DIR}" 2>&1 | tee "${LOG_DIR}/docker_compose_ps.log"

echo "[BWP] waiting ${RUN_WAIT_SECONDS}s before log collection"
sleep "${RUN_WAIT_SECONDS}"

if [[ -n "${BWP_TRIGGER_SEQUENCE}" ]]; then
  for bwp_id in ${BWP_TRIGGER_SEQUENCE}; do
    echo "[BWP] trigger BWP switch to ${bwp_id}" | tee -a "${LOG_DIR}/bwp_trigger_commands.log"
    set +e
    docker exec rfsim5g-oai-gnb_redcap bash -lc "if command -v nc >/dev/null 2>&1; then printf 'ci trigger_bwp_switch ${bwp_id}\n' | nc -N 127.0.0.1 9091; else exec 3<>/dev/tcp/127.0.0.1/9091; printf 'ci trigger_bwp_switch ${bwp_id}\n' >&3; timeout 2 cat <&3 || true; exec 3>&-; fi" \
      >> "${LOG_DIR}/bwp_trigger_commands.log" 2>&1
    trigger_rc="$?"
    set -e
    if [[ "${trigger_rc}" -ne 0 ]]; then
      TRIGGER_FAILURES=$((TRIGGER_FAILURES + 1))
      echo "[BWP][WARN] trigger BWP ${bwp_id} failed with rc=${trigger_rc}" | tee -a "${LOG_DIR}/bwp_trigger_commands.log"
    fi
    sleep "${BWP_TRIGGER_DELAY_SECONDS}"
  done
fi

redcap_compose_ps "${COMPOSE_DIR}" 2>&1 | tee "${LOG_DIR}/docker_compose_ps_after_wait.log"
"${SCRIPT_DIR}/collect_runtime_artifacts.sh" --mode bwp --log-dir "${LOG_DIR}" --scenario "${RUNTIME_SCENARIO}"

GNB_FULL_LOG="${LOG_DIR}/container_logs/full/gnb.log"
if [[ -f "${GNB_FULL_LOG}" ]] && grep -E "Segmentation fault|core dumped|AddressSanitizer|AssertFatal" "${GNB_FULL_LOG}" >/dev/null; then
  RUNTIME_FAILURES=$((RUNTIME_FAILURES + 1))
  echo "[BWP][ERROR] gNB runtime failure marker found in ${GNB_FULL_LOG}" | tee -a "${LOG_DIR}/bwp_trigger_commands.log"
fi

if [[ "${STOP_AFTER_RUN}" == "1" ]]; then
  redcap_compose_stop "${COMPOSE_DIR}" "${SERVICE_ARGS[@]}" 2>&1 | tee "${LOG_DIR}/docker_compose_stop.log"
fi

if [[ "${TRIGGER_FAILURES}" -ne 0 || "${RUNTIME_FAILURES}" -ne 0 ]]; then
  echo "[BWP][ERROR] trigger_failures=${TRIGGER_FAILURES} runtime_failures=${RUNTIME_FAILURES}" | tee -a "${LOG_DIR}/bwp_trigger_commands.log"
  exit 1
fi
