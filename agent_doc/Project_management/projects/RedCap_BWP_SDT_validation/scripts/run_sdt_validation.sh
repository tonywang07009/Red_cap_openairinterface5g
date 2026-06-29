#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${PROJECT_DIR}/../../../.." && pwd)"
source "${SCRIPT_DIR}/redcap_runtime_common.sh"

COMPOSE_DIR="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap"
CONFIG_FILE="${PROJECT_DIR}/configs/SDT_local_matrix.yaml"
INTERFACE_RUNNER="${REPO_ROOT}/redcap_interface/mmtc.menu.bash"
INTERFACE_SUBCOMMAND="${MMTC_SDT_MENU_SUBCOMMAND:-gate3}"
POLICY_FILE="${REDCAP_POLICY_HOST_FILE:-${COMPOSE_DIR}/control/redcap_policy_case_a.yaml}"
RUN_MODE="${1:---dry-run}"
RUN_ID="${RUN_ID:-$(date +%Y%m%d_%H%M%S)}"
LOG_DIR="${REPO_ROOT}/test_log/redcap_bwp_sdt_validation/${RUN_ID}_sdt"
RUNTIME_SCENARIO="${RUNTIME_SCENARIO:-local_rfsim_ue2_minimal_sdt}"
COMPILER_LOG_DIR="${REPO_ROOT}/test_log/compiler_logs"
MMTC_SAMPLE_UES="${MMTC_SAMPLE_UES:-2}"
MMTC_TOTAL_UES="${MMTC_TOTAL_UES:-29}"
MMTC_SLEEP_AFTER_UP="${MMTC_SLEEP_AFTER_UP:-25}"
MMTC_GNB_WARMUP="${MMTC_GNB_WARMUP:-5}"

redcap_validate_run_mode "${RUN_MODE}"

mkdir -p "${LOG_DIR}"

redcap_export_local_image_defaults
redcap_export_rf_defaults
export REDCAP_CASE="${REDCAP_CASE:-case_a}"
export REDCAP_POLICY_HOST_FILE="${POLICY_FILE}"
export MMTC_TOTAL_UES
export MMTC_SAMPLE_UES
export MMTC_SLEEP_AFTER_UP
export MMTC_GNB_WARMUP
export MMTC_RRC_INACTIVE_GATE1_TRIGGER="${MMTC_RRC_INACTIVE_GATE1_TRIGGER:-1}"
export MMTC_RRC_INACTIVE_GATE2_RESUME_TRIGGER="${MMTC_RRC_INACTIVE_GATE2_RESUME_TRIGGER:-0}"
export MMTC_RRC_INACTIVE_GATE3_CG_CONFIG="${MMTC_RRC_INACTIVE_GATE3_CG_CONFIG:-1}"
export MMTC_RRC_INACTIVE_GATE4_FORCE_FALLBACK="${MMTC_RRC_INACTIVE_GATE4_FORCE_FALLBACK:-0}"
export MMTC_RA_ACCESS_STEPS="${MMTC_RA_ACCESS_STEPS:-4}"
export MMTC_CGCFG_NOFREE="${MMTC_CGCFG_NOFREE:-0}"
export MMTC_CGCFG_DEFER_FREE_SLOTS="${MMTC_CGCFG_DEFER_FREE_SLOTS:-0}"

cat > "${LOG_DIR}/run_manifest.txt" <<EOF
experiment=RA_SDT_vs_CG_SDT_small_data
config=${CONFIG_FILE}
compose_root=${COMPOSE_DIR}
runtime_delegate=${INTERFACE_RUNNER} ${INTERFACE_SUBCOMMAND}
runtime_baseline_project=agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1
run_mode=${RUN_MODE}
REGISTRY=${REGISTRY}
GNB_IMG=${GNB_IMG}
NRUE_IMG=${NRUE_IMG}
TAG=${TAG}
runtime_scenario=${RUNTIME_SCENARIO}
REDCAP_CASE=${REDCAP_CASE}
REDCAP_POLICY_HOST_FILE=${REDCAP_POLICY_HOST_FILE}
MMTC_TOTAL_UES=${MMTC_TOTAL_UES}
MMTC_SAMPLE_UES=${MMTC_SAMPLE_UES}
MMTC_SLEEP_AFTER_UP=${MMTC_SLEEP_AFTER_UP}
MMTC_GNB_WARMUP=${MMTC_GNB_WARMUP}
MMTC_REDCAP_ENABLE=${MMTC_REDCAP_ENABLE}
MMTC_REDCAP_NUM_RX=${MMTC_REDCAP_NUM_RX}
MMTC_REDCAP_HALF_DUPLEX=${MMTC_REDCAP_HALF_DUPLEX}
MMTC_N_RB_DL=${MMTC_N_RB_DL}
MMTC_NUMEROLOGY=${MMTC_NUMEROLOGY}
MMTC_RF_FREQ=${MMTC_RF_FREQ}
MMTC_SSB_START=${MMTC_SSB_START}
MMTC_RRC_INACTIVE_GATE1_TRIGGER=${MMTC_RRC_INACTIVE_GATE1_TRIGGER}
MMTC_RRC_INACTIVE_GATE2_RESUME_TRIGGER=${MMTC_RRC_INACTIVE_GATE2_RESUME_TRIGGER}
MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=${MMTC_RRC_INACTIVE_GATE3_CG_CONFIG}
MMTC_RRC_INACTIVE_GATE4_FORCE_FALLBACK=${MMTC_RRC_INACTIVE_GATE4_FORCE_FALLBACK}
MMTC_RA_ACCESS_STEPS=${MMTC_RA_ACCESS_STEPS}
MMTC_CGCFG_NOFREE=${MMTC_CGCFG_NOFREE}
MMTC_CGCFG_DEFER_FREE_SLOTS=${MMTC_CGCFG_DEFER_FREE_SLOTS}
note=SDT runtime delegates to the existing redcap_interface Gate3 flow; this paper project only collects logs and merges paper-facing metrics.
EOF

echo "[SDT] manifest: ${LOG_DIR}/run_manifest.txt"
echo "[SDT] config: ${CONFIG_FILE}"
echo "[SDT] delegate: ${INTERFACE_RUNNER} ${INTERFACE_SUBCOMMAND}"
echo "[SDT] sample UEs: ${MMTC_SAMPLE_UES}"

if [[ "${RUN_MODE}" == "--dry-run" ]]; then
  echo "[SDT] dry-run only. Use --run to delegate to redcap_interface Gate3."
  exit 0
fi

read -r -a SAMPLE_UE_ARGS <<< "${MMTC_SAMPLE_UES}"
FIRST_SAMPLE_UE="${SAMPLE_UE_ARGS[0]}"
START_EPOCH="$(date +%s)"
CONSOLE_LOG="${LOG_DIR}/redcap_interface_${INTERFACE_SUBCOMMAND}_console.log"

set +e
bash "${INTERFACE_RUNNER}" "${INTERFACE_SUBCOMMAND}" 2>&1 | tee "${CONSOLE_LOG}"
DELEGATE_RC="${PIPESTATUS[0]}"
set -e

CONTAINER_LOG_DIR="${LOG_DIR}/container_logs"
FULL_LOG_DIR="${CONTAINER_LOG_DIR}/full"
mkdir -p "${FULL_LOG_DIR}"

GNB_LOG="$(find "${COMPILER_LOG_DIR}" -maxdepth 1 -type f -name 'mmtc_smoke_*_gnb.log' -newermt "@${START_EPOCH}" -print | sort | tail -n 1 || true)"
UE_LOG="$(find "${COMPILER_LOG_DIR}" -maxdepth 1 -type f -name "mmtc_smoke_*_ue${FIRST_SAMPLE_UE}_docker.log" -newermt "@${START_EPOCH}" -print | sort | tail -n 1 || true)"

if [[ -n "${GNB_LOG}" ]]; then
  cp "${GNB_LOG}" "${FULL_LOG_DIR}/gnb.log"
else
  echo "gNB log not found after epoch ${START_EPOCH}" > "${FULL_LOG_DIR}/gnb.log"
fi

if [[ -n "${UE_LOG}" ]]; then
  cp "${UE_LOG}" "${FULL_LOG_DIR}/ue2.log"
else
  echo "UE${FIRST_SAMPLE_UE} log not found after epoch ${START_EPOCH}" > "${FULL_LOG_DIR}/ue2.log"
fi

cp "${CONSOLE_LOG}" "${FULL_LOG_DIR}/redcap_interface_gate3_console.log"
tail -n "${TAIL_LINES:-400}" "${FULL_LOG_DIR}/gnb.log" > "${CONTAINER_LOG_DIR}/gnb_tail.log" || true
tail -n "${TAIL_LINES:-400}" "${FULL_LOG_DIR}/ue2.log" > "${CONTAINER_LOG_DIR}/ue2_tail.log" || true

redcap_extract_and_merge_runtime_metrics "${SCRIPT_DIR}" "${PROJECT_DIR}" sdt "${LOG_DIR}" "${RUNTIME_SCENARIO}"

echo "[SDT] delegated runner rc: ${DELEGATE_RC}"
echo "[SDT] copied gNB log: ${GNB_LOG:-not-found}"
echo "[SDT] copied UE log: ${UE_LOG:-not-found}"
exit "${DELEGATE_RC}"
