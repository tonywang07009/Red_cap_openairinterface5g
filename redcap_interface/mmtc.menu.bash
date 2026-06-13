#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/..")
LIB_DIR="${SCRIPT_DIR}/bash_library"

DEFAULT_GNB_CONFIG="${REPO_ROOT}/redcap_library/library_gnb_config/gnb_redcap_mmtc_case_b_final.yaml"
DEFAULT_CN_COMPOSE="/home/tonywang/OAI/oai-cn5g/docker-compose.yaml"
BASE_COMPOSE="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml"
OVERLAY_COMPOSE="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml"
DEFAULT_POLICY="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/control/redcap_policy_case_a.yaml"
CONTRACT_FILE="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/control/redcap_control_contract.yaml"

normalize_bool()
{
  case "${1,,}" in
    1|true|t|yes|y|on|enable|enabled) printf '1\n' ;;
    0|false|f|no|n|off|disable|disabled) printf '0\n' ;;
    *) printf '0\n' ;;
  esac
}

GNB_CONFIG="${GNB_REDCAP_CONFIG:-${DEFAULT_GNB_CONFIG}}"
CN_COMPOSE="${MMTC_CN_COMPOSE:-${DEFAULT_CN_COMPOSE}}"
TOTAL_UES="${MMTC_TOTAL_UES:-29}"
SAMPLE_UES="${MMTC_SAMPLE_UES:-1}"
REDCAP_CASE="${REDCAP_CASE:-case_a}"
POLICY_FILE="${REDCAP_POLICY_HOST_FILE:-${DEFAULT_POLICY}}"
PUSCH_256QAM="$(normalize_bool "${MMTC_PUSCH_256QAM:-0}")"
PDSCH_256QAM="$(normalize_bool "${MMTC_PDSCH_256QAM:-0}")"
REDCAP_NUM_RX="${MMTC_REDCAP_NUM_RX:-1}"
REDCAP_HALF_DUPLEX="$(normalize_bool "${MMTC_REDCAP_HALF_DUPLEX:-1}")"
DRX_PROFILE="${MMTC_DRX_PROFILE:-off}"
EDRX_CYCLE_S="${MMTC_EDRX_CYCLE_S:-0}"
EDRX_PTW_S="${MMTC_EDRX_PTW_S:-0}"
PSM_T3324_S="${MMTC_PSM_T3324_ACTIVE_TIME_S:-0}"
PSM_T3512_S="${MMTC_PSM_T3512_TAU_S:-0}"
GATE1="${MMTC_RRC_INACTIVE_GATE1_TRIGGER:-0}"
GATE2="${MMTC_RRC_INACTIVE_GATE2_RESUME_TRIGGER:-0}"
GATE3="${MMTC_RRC_INACTIVE_GATE3_CG_CONFIG:-0}"
GATE4="${MMTC_RRC_INACTIVE_GATE4_FORCE_FALLBACK:-0}"

print_header()
{
  cat <<EOF

RedCap mMTC Daily RFsim Menu
Repo          : ${REPO_ROOT}
gNB config    : ${GNB_CONFIG}
CN compose    : ${CN_COMPOSE}
Policy        : ${POLICY_FILE}
Contract      : ${CONTRACT_FILE}
Case          : ${REDCAP_CASE}
Total/Sample  : ${TOTAL_UES} / ${SAMPLE_UES}
PUSCH/PDSCH   : 256QAM=${PUSCH_256QAM}/${PDSCH_256QAM}
RedCap RX/HD  : num_rx=${REDCAP_NUM_RX}, half_duplex=${REDCAP_HALF_DUPLEX}
Low power     : drx=${DRX_PROFILE}, edrx_cycle_s=${EDRX_CYCLE_S}, edrx_ptw_s=${EDRX_PTW_S}, psm_t3324_s=${PSM_T3324_S}, psm_t3512_s=${PSM_T3512_S}
Gate flags    : gate1=${GATE1}, gate2=${GATE2}, gate3=${GATE3}, gate4=${GATE4}

EOF
}

pause_for_enter()
{
  read -r -p "Press Enter to continue..."
}

require_file()
{
  local path="$1"
  local label="$2"
  if [ ! -f "${path}" ]; then
    echo "[ERROR] Missing ${label}: ${path}" >&2
    return 1
  fi
}

check_inputs()
{
  require_file "${GNB_CONFIG}" "gNB config"
  require_file "${CN_COMPOSE}" "CN compose"
  require_file "${POLICY_FILE}" "policy file"
  require_file "${CONTRACT_FILE}" "control contract"
  require_file "${BASE_COMPOSE}" "base compose"
  require_file "${OVERLAY_COMPOSE}" "mMTC overlay compose"
}

show_mounts()
{
  check_inputs
  echo "[INFO] Runtime files"
  printf 'gNB config : %s\n' "${GNB_CONFIG}"
  printf 'CN compose : %s\n' "${CN_COMPOSE}"
  printf 'Policy     : %s\n' "${POLICY_FILE}"
  printf 'Contract   : %s\n' "${CONTRACT_FILE}"
  echo
  echo "[INFO] Compose gNB mount excerpt"
  GNB_REDCAP_CONFIG="${GNB_CONFIG}" REDCAP_POLICY_HOST_FILE="${POLICY_FILE}" docker compose \
    --env-file /dev/null \
    -f "${BASE_COMPOSE}" \
    -f "${OVERLAY_COMPOSE}" \
    config | sed -n '/oai-gnb:/,/oai-nr-ue1:/p' | rg -n 'source:|target:|gnb.yaml|policy.yaml' || true
}

configure_runtime()
{
  local value
  read -r -p "gNB config [${GNB_CONFIG}]: " value
  GNB_CONFIG="${value:-${GNB_CONFIG}}"
  read -r -p "CN compose [${CN_COMPOSE}]: " value
  CN_COMPOSE="${value:-${CN_COMPOSE}}"
  read -r -p "Policy file [${POLICY_FILE}]: " value
  POLICY_FILE="${value:-${POLICY_FILE}}"
  read -r -p "Case [${REDCAP_CASE}]: " value
  REDCAP_CASE="${value:-${REDCAP_CASE}}"
  read -r -p "Total UEs [${TOTAL_UES}]: " value
  TOTAL_UES="${value:-${TOTAL_UES}}"
  read -r -p "Sample UEs [${SAMPLE_UES}]: " value
  SAMPLE_UES="${value:-${SAMPLE_UES}}"
}

configure_radio()
{
  local value
  read -r -p "Enable UL/PUSCH 256QAM 0/1 [${PUSCH_256QAM}]: " value
  PUSCH_256QAM="$(normalize_bool "${value:-${PUSCH_256QAM}}")"
  read -r -p "Enable DL/PDSCH 256QAM 0/1 [${PDSCH_256QAM}]: " value
  PDSCH_256QAM="$(normalize_bool "${value:-${PDSCH_256QAM}}")"
  read -r -p "RedCap RX count 1/2 [${REDCAP_NUM_RX}]: " value
  REDCAP_NUM_RX="${value:-${REDCAP_NUM_RX}}"
  read -r -p "Half duplex 0/1 [${REDCAP_HALF_DUPLEX}]: " value
  REDCAP_HALF_DUPLEX="$(normalize_bool "${value:-${REDCAP_HALF_DUPLEX}}")"
}

configure_low_power()
{
  local value
  read -r -p "DRX profile off/low_latency/balanced/power_saving [${DRX_PROFILE}]: " value
  DRX_PROFILE="${value:-${DRX_PROFILE}}"
  read -r -p "eDRX cycle seconds, 0 disables [${EDRX_CYCLE_S}]: " value
  EDRX_CYCLE_S="${value:-${EDRX_CYCLE_S}}"
  read -r -p "eDRX PTW seconds, 0 disables [${EDRX_PTW_S}]: " value
  EDRX_PTW_S="${value:-${EDRX_PTW_S}}"
  read -r -p "PSM T3324 active time seconds, 0 disables [${PSM_T3324_S}]: " value
  PSM_T3324_S="${value:-${PSM_T3324_S}}"
  read -r -p "PSM T3512 TAU seconds, 0 disables [${PSM_T3512_S}]: " value
  PSM_T3512_S="${value:-${PSM_T3512_S}}"
}

configure_gates()
{
  local value
  read -r -p "Gate1 RRC inactive trigger 0/1 [${GATE1}]: " value
  GATE1="$(normalize_bool "${value:-${GATE1}}")"
  read -r -p "Gate2 resume trigger 0/1 [${GATE2}]: " value
  GATE2="$(normalize_bool "${value:-${GATE2}}")"
  read -r -p "Gate3 configured grant trigger 0/1 [${GATE3}]: " value
  GATE3="$(normalize_bool "${value:-${GATE3}}")"
  read -r -p "Gate4 force TA/RSRP fallback 0/1 [${GATE4}]: " value
  GATE4="$(normalize_bool "${value:-${GATE4}}")"
}

run_smoke()
{
  check_inputs
  env \
    GNB_REDCAP_CONFIG="${GNB_CONFIG}" \
    MMTC_CN_COMPOSE="${CN_COMPOSE}" \
    MMTC_TOTAL_UES="${TOTAL_UES}" \
    MMTC_SAMPLE_UES="${SAMPLE_UES}" \
    MMTC_REDCAP_NUM_RX="${REDCAP_NUM_RX}" \
    MMTC_REDCAP_HALF_DUPLEX="${REDCAP_HALF_DUPLEX}" \
    MMTC_PUSCH_256QAM="${PUSCH_256QAM}" \
    MMTC_PDSCH_256QAM="${PDSCH_256QAM}" \
    MMTC_DRX_PROFILE="${DRX_PROFILE}" \
    MMTC_EDRX_CYCLE_S="${EDRX_CYCLE_S}" \
    MMTC_EDRX_PTW_S="${EDRX_PTW_S}" \
    MMTC_PSM_T3324_ACTIVE_TIME_S="${PSM_T3324_S}" \
    MMTC_PSM_T3512_TAU_S="${PSM_T3512_S}" \
    REDCAP_CASE="${REDCAP_CASE}" \
    REDCAP_POLICY_HOST_FILE="${POLICY_FILE}" \
    MMTC_RRC_INACTIVE_GATE1_TRIGGER="${GATE1}" \
    MMTC_RRC_INACTIVE_GATE2_RESUME_TRIGGER="${GATE2}" \
    MMTC_RRC_INACTIVE_GATE3_CG_CONFIG="${GATE3}" \
    MMTC_RRC_INACTIVE_GATE4_FORCE_FALLBACK="${GATE4}" \
    bash "${LIB_DIR}/fc_mmtc_smoke_validation.sh"
}

docker_status()
{
  docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}' | rg 'oai|rfsim|RIC|mysql|ims' || true
}

docker_down()
{
  check_inputs
  docker compose --env-file /dev/null -f "${BASE_COMPOSE}" -f "${OVERLAY_COMPOSE}" down --remove-orphans
  docker compose --env-file /dev/null -f "${CN_COMPOSE}" down --remove-orphans || true
}

run_rebuild()
{
  bash "${LIB_DIR}/fc_rebuild_local_oai_images.sh"
}

run_inspect()
{
  bash "${LIB_DIR}/fc_inspect_gnb_image.sh"
}

dispatch_cli()
{
  case "${1:-}" in
    smoke) run_smoke ;;
    gate3)
      GATE1=1
      GATE2=0
      GATE3=1
      GATE4=0
      run_smoke
      ;;
    gate4)
      GATE1=1
      GATE2=0
      GATE3=1
      GATE4=1
      run_smoke
      ;;
    rebuild) run_rebuild ;;
    inspect) run_inspect ;;
    status) docker_status ;;
    down) docker_down ;;
    redcap-vs-normal) shift; bash "${LIB_DIR}/fc_runtime_menu_legacy.sh" redcap-vs-normal "$@" ;;
    "") return 1 ;;
    *)
      echo "[ERROR] Unknown subcommand: $1" >&2
      echo "Known: smoke, gate3, gate4, rebuild, inspect, status, down, redcap-vs-normal" >&2
      return 2
      ;;
  esac
}

main_menu()
{
  local choice
  while true; do
    print_header
    cat <<'EOF'
1) Show mounted runtime files
2) Configure runtime paths / UE sample
3) Configure 256QAM and 1RX/2RX
4) Configure DRX/eDRX/PSM timers
5) Configure RRC_INACTIVE Gate flags
6) Run smoke validation
7) Run Gate3 Gate2-OFF smoke
8) Run Gate4 TA/RSRP fallback smoke
9) Rebuild local OAI Docker images
10) Inspect local gNB image markers
11) Docker status
12) Docker down
q) Quit
EOF
    read -r -p "Choice: " choice
    case "${choice}" in
      1) show_mounts; pause_for_enter ;;
      2) configure_runtime ;;
      3) configure_radio ;;
      4) configure_low_power ;;
      5) configure_gates ;;
      6) run_smoke; pause_for_enter ;;
      7) GATE1=1; GATE2=0; GATE3=1; GATE4=0; run_smoke; pause_for_enter ;;
      8) GATE1=1; GATE2=0; GATE3=1; GATE4=1; run_smoke; pause_for_enter ;;
      9) run_rebuild; pause_for_enter ;;
      10) run_inspect; pause_for_enter ;;
      11) docker_status; pause_for_enter ;;
      12) docker_down; pause_for_enter ;;
      q|Q) exit 0 ;;
      *) echo "[WARN] Unknown choice: ${choice}" ;;
    esac
  done
}

if [ "$#" -gt 0 ]; then
  dispatch_cli "$@"
else
  main_menu
fi
