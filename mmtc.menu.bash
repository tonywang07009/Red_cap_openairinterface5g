#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT="${SCRIPT_DIR}"
INTERFACE_DIR="${REPO_ROOT}/redcap_interface"
LIB_DIR="${INTERFACE_DIR}/bash_library"

DEFAULT_GNB_CONFIG="${REPO_ROOT}/redcap_library/library_gnb_config/gnb_redcap_mmtc_case_b_final.yaml"
DEFAULT_CN_COMPOSE="${REPO_ROOT}/oai-cn5g/docker-compose.yaml"
BASE_COMPOSE="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml"
RUNTIME_CONFIG_DIR="${REPO_ROOT}/test_log/runtime_configs"
RUN_ID="${MMTC_RUN_ID:-mmtc_menu_$(date +%Y%m%d_%H%M%S)}"
OVERLAY_GENERATOR="${LIB_DIR}/generate_mmtc_overlay.sh"
OVERLAY_COMPOSE="${MMTC_OVERLAY_COMPOSE:-${RUNTIME_CONFIG_DIR}/${RUN_ID}_overlay.yml}"
DEFAULT_POLICY="${REPO_ROOT}/redcap_interface/control/redcap_policy_case_a.yaml"
CONTRACT_FILE="${REPO_ROOT}/redcap_interface/control/redcap_control_contract.yaml"
DISPLAY_MENU="${INTERFACE_DIR}/mmtc.display.bash"
INSTALLER="${LIB_DIR}/fc_install_redcap.sh"
PROFILE_VERSION=1

show_help()
{
  cat <<'EOF'
RedCap mMTC RFsim 操作選單

用法：
  ./mmtc.menu.bash [子命令]

主要子命令：
  install [--check|--help]       互動安裝，預設以乾淨 1 UE smoke 驗收
  intro                         顯示安全的專案介紹與文件入口
  performance                   顯示已驗證的 paper/效能證據
  performance reproduce         明確進入既有重現工具
  experiment [profile-path]     互動建立 experiment profile，不啟動 Docker
  preview-profile <path>        驗證並顯示 profile，不啟動 Docker
  run-profile <path> [mode]     以 smoke、gate3 或 gate4 執行 profile

UE 容量固定為 56。使用 MMTC_ACTIVE_UES 選擇本次實際啟動的 UE；
可用逗號、空白或兩者混合分隔，合法編號為 1..56，且不可重複。

範例：
  MMTC_ACTIVE_UES="1" ./mmtc.menu.bash smoke
  MMTC_ACTIVE_UES="1 29 56" ./mmtc.menu.bash smoke

相容子命令：smoke、gate3、gate4、rebuild、inspect、status、down、redcap-vs-normal

RedCap mMTC RFsim operator menu

Usage:
  ./mmtc.menu.bash [subcommand]

Primary subcommands:
  install [--check|--help]       Install interactively; accept with a clean 1 UE smoke
  intro                         Show the safe project introduction and doc routes
  performance                   Show accepted paper/performance evidence
  performance reproduce         Explicitly enter the existing reproduction tools
  experiment [profile-path]     Create an experiment profile without starting Docker
  preview-profile <path>        Validate and show a profile without starting Docker
  run-profile <path> [mode]     Run a profile with smoke, gate3, or gate4

UE capacity is fixed at 56. MMTC_ACTIVE_UES selects the UE services activated
for this run. Separate indices with commas, whitespace, or both. Valid unique
indices are 1..56.

Examples:
  MMTC_ACTIVE_UES="1" ./mmtc.menu.bash smoke
  MMTC_ACTIVE_UES="1 29 56" ./mmtc.menu.bash smoke

Compatibility subcommands: smoke, gate3, gate4, rebuild, inspect, status, down, redcap-vs-normal
EOF
}

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
TOTAL_UES=56
ACTIVE_UES="${MMTC_ACTIVE_UES-1}"
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
N_RB_DL="${MMTC_N_RB_DL:-106}"
START_XAPP="$(normalize_bool "${MMTC_START_XAPP:-0}")"
DAPP_ENABLE="$(normalize_bool "${OAI_REDCAP_DAPP_GATE_D_MARKER:-0}")"

show_intro()
{
  cat <<EOF
RedCap 專案介紹 / Project introduction

- 目前拓撲 / Current topology: single monolithic gNB + RFsim
- UE 容量 / UE capacity: fixed UE1..UE56; choose active UEs per run
- 控制責任 / Control ownership: xApp hints -> dApp/gNB guard -> gNB apply
- 未支援 / Unsupported in profile v1: multiple gNBs and CU/DU split

繁體中文：${REPO_ROOT}/README.zh-TW.md
English: ${REPO_ROOT}/README.en.md
操作介面 / Operator interface: ${REPO_ROOT}/redcap_interface/Doc/
新手教學 / Beginner guide: ${REPO_ROOT}/redcap_doc/manuals/redcap_zero_to_build_and_run_guide.zh-TW.md
EOF
}

show_performance_evidence()
{
  cat <<EOF
已驗證效能證據 / Accepted performance evidence

- Paper 07 TDD reproduction: redcap_doc/evluation_recover/paper07_tdd_reproduction_tutorial.{zh-TW,en}.md
- Paper 08 Fig. 9 channel model: redcap_interface/mmtc.display.bash paper08
- Paper 11 live/Table 3: redcap_doc/evluation_recover/paper11_*_tutorial.{zh-TW,en}.md
- SDT A/B: redcap_interface/mmtc.display.bash sdt-ab
- Accepted reports: redcap_library/library_reports_summary/

以上只顯示證據，不啟動 Docker。
This command only shows evidence; it does not start Docker.

明確進入重現工具 / Explicitly enter reproduction tools:
  ./mmtc.menu.bash performance reproduce
EOF
}

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
Capacity/Active: ${TOTAL_UES} / ${ACTIVE_UES}
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

validate_active_ues()
{
  canonicalize_active_ues "${ACTIVE_UES}" >/dev/null
}

canonicalize_active_ues()
{
  local raw="$1"
  local ue_idx
  local -a active_ues=()
  declare -A seen=()

  mapfile -t active_ues < <(printf '%s\n' "${raw}" | tr ', ' '\n' | sed '/^$/d')
  if [ "${#active_ues[@]}" -eq 0 ]; then
    echo "[ERROR] MMTC_ACTIVE_UES 不可為空 / must not be empty." >&2
    return 2
  fi

  for ue_idx in "${active_ues[@]}"; do
    if ! [[ "${ue_idx}" =~ ^[0-9]+$ ]] || (( 10#${ue_idx} < 1 || 10#${ue_idx} > TOTAL_UES )); then
      echo "[ERROR] 無效的 UE 編號 / invalid UE index '${ue_idx}'; expected 1..${TOTAL_UES}." >&2
      return 2
    fi
    ue_idx=$((10#${ue_idx}))
    if [ -n "${seen[${ue_idx}]:-}" ]; then
      echo "[ERROR] UE 編號不可重複 / duplicate UE index: ${ue_idx}." >&2
      return 2
    fi
    seen[${ue_idx}]=1
  done

  local IFS=,
  printf '%s\n' "${active_ues[*]}"
}

validate_profile_path_value()
{
  local value="$1"
  [[ "${value}" =~ ^[/A-Za-z0-9._-]+$ ]]
}

validate_loaded_profile()
{
  local required
  local -a required_keys=(
    REDCAP_EXPERIMENT_PROFILE_VERSION REDCAP_EXPERIMENT_NAME REDCAP_TOPOLOGY REDCAP_GNB_COUNT
    REDCAP_CU_DU_SPLIT MMTC_TOTAL_UES MMTC_ACTIVE_UES MMTC_N_RB_DL GNB_REDCAP_CONFIG
    MMTC_CN_COMPOSE REDCAP_CASE REDCAP_POLICY_HOST_FILE REDCAP_CONTROL_CONTRACT_FILE
    MMTC_START_XAPP OAI_REDCAP_DAPP_GATE_D_MARKER
  )

  for required in "${required_keys[@]}"; do
    if [ -z "${PROFILE_SEEN[${required}]:-}" ]; then
      echo "[ERROR] Missing profile key: ${required}" >&2
      return 2
    fi
  done

  [ "${PROFILE_VERSION_VALUE}" = "${PROFILE_VERSION}" ] || {
    echo "[ERROR] Unsupported profile version: ${PROFILE_VERSION_VALUE}" >&2
    return 2
  }
  [[ "${PROFILE_NAME}" =~ ^[A-Za-z0-9._-]+$ ]] || {
    echo "[ERROR] Invalid experiment name: ${PROFILE_NAME}" >&2
    return 2
  }
  [ "${PROFILE_TOPOLOGY}" = "single_gnb_rfsim" ] && [ "${PROFILE_GNB_COUNT}" = "1" ] && [ "${PROFILE_CU_DU_SPLIT}" = "0" ] || {
    echo "[ERROR] Profile v1 supports only one monolithic gNB; CU/DU split is unsupported." >&2
    return 2
  }
  [ "${PROFILE_TOTAL_UES}" = "56" ] || {
    echo "[ERROR] Profile capacity must be 56." >&2
    return 2
  }
  TOTAL_UES=56
  PROFILE_ACTIVE_UES="$(canonicalize_active_ues "${PROFILE_ACTIVE_UES}")" || return 2
  [[ "${PROFILE_N_RB_DL}" =~ ^(51|106)$ ]] || {
    echo "[ERROR] MMTC_N_RB_DL must be 51 or 106." >&2
    return 2
  }
  [[ "${PROFILE_REDCAP_CASE}" =~ ^case_[ab]$ ]] || {
    echo "[ERROR] REDCAP_CASE must be case_a or case_b." >&2
    return 2
  }
  [[ "${PROFILE_START_XAPP}" =~ ^[01]$ ]] && [[ "${PROFILE_DAPP_ENABLE}" =~ ^[01]$ ]] || {
    echo "[ERROR] xApp/dApp flags must be 0 or 1." >&2
    return 2
  }

  local path
  for path in "${PROFILE_GNB_CONFIG}" "${PROFILE_CN_COMPOSE}" "${PROFILE_POLICY_FILE}" "${PROFILE_CONTRACT_FILE}"; do
    validate_profile_path_value "${path}" && [ -f "${path}" ] || {
      echo "[ERROR] Invalid or missing profile path: ${path}" >&2
      return 2
    }
  done
}

load_profile()
{
  local profile_path="$1"
  local line key value
  declare -gA PROFILE_SEEN=()

  require_file "${profile_path}" "experiment profile"
  while IFS= read -r line || [ -n "${line}" ]; do
    [ -n "${line}" ] || continue
    [[ "${line}" == \#* ]] && continue
    [[ "${line}" == *=* ]] || {
      echo "[ERROR] Invalid profile line: ${line}" >&2
      return 2
    }
    key=${line%%=*}
    value=${line#*=}
    [ -n "${key}" ] && [ -n "${value}" ] || {
      echo "[ERROR] Empty profile key/value is not allowed." >&2
      return 2
    }
    if [ -n "${PROFILE_SEEN[${key}]:-}" ]; then
      echo "[ERROR] Duplicate profile key: ${key}" >&2
      return 2
    fi
    PROFILE_SEEN[${key}]=1
    case "${key}" in
      REDCAP_EXPERIMENT_PROFILE_VERSION) PROFILE_VERSION_VALUE="${value}" ;;
      REDCAP_EXPERIMENT_NAME) PROFILE_NAME="${value}" ;;
      REDCAP_TOPOLOGY) PROFILE_TOPOLOGY="${value}" ;;
      REDCAP_GNB_COUNT) PROFILE_GNB_COUNT="${value}" ;;
      REDCAP_CU_DU_SPLIT) PROFILE_CU_DU_SPLIT="${value}" ;;
      MMTC_TOTAL_UES) PROFILE_TOTAL_UES="${value}" ;;
      MMTC_ACTIVE_UES) PROFILE_ACTIVE_UES="${value}" ;;
      MMTC_N_RB_DL) PROFILE_N_RB_DL="${value}" ;;
      GNB_REDCAP_CONFIG) PROFILE_GNB_CONFIG="${value}" ;;
      MMTC_CN_COMPOSE) PROFILE_CN_COMPOSE="${value}" ;;
      REDCAP_CASE) PROFILE_REDCAP_CASE="${value}" ;;
      REDCAP_POLICY_HOST_FILE) PROFILE_POLICY_FILE="${value}" ;;
      REDCAP_CONTROL_CONTRACT_FILE) PROFILE_CONTRACT_FILE="${value}" ;;
      MMTC_START_XAPP) PROFILE_START_XAPP="${value}" ;;
      OAI_REDCAP_DAPP_GATE_D_MARKER) PROFILE_DAPP_ENABLE="${value}" ;;
      *)
        echo "[ERROR] Unknown profile key: ${key}" >&2
        return 2
        ;;
    esac
  done < "${profile_path}"

  validate_loaded_profile
}

print_loaded_profile()
{
  cat <<EOF
REDCAP_EXPERIMENT_PROFILE_VERSION=${PROFILE_VERSION_VALUE}
REDCAP_EXPERIMENT_NAME=${PROFILE_NAME}
REDCAP_TOPOLOGY=${PROFILE_TOPOLOGY}
REDCAP_GNB_COUNT=${PROFILE_GNB_COUNT}
REDCAP_CU_DU_SPLIT=${PROFILE_CU_DU_SPLIT}
MMTC_TOTAL_UES=${PROFILE_TOTAL_UES}
MMTC_ACTIVE_UES=${PROFILE_ACTIVE_UES}
MMTC_N_RB_DL=${PROFILE_N_RB_DL}
GNB_REDCAP_CONFIG=${PROFILE_GNB_CONFIG}
MMTC_CN_COMPOSE=${PROFILE_CN_COMPOSE}
REDCAP_CASE=${PROFILE_REDCAP_CASE}
REDCAP_POLICY_HOST_FILE=${PROFILE_POLICY_FILE}
REDCAP_CONTROL_CONTRACT_FILE=${PROFILE_CONTRACT_FILE}
MMTC_START_XAPP=${PROFILE_START_XAPP}
OAI_REDCAP_DAPP_GATE_D_MARKER=${PROFILE_DAPP_ENABLE}
EOF
}

preview_profile()
{
  load_profile "$1"
  print_loaded_profile
}

create_experiment_profile()
{
  local output_path="${1:-${RUNTIME_CONFIG_DIR}/${RUN_ID}.profile.env}"
  local output_dir
  local value

  output_dir=$(realpath -m "$(dirname "${output_path}")")
  [ "${output_dir}" = "${RUNTIME_CONFIG_DIR}" ] || {
    echo "[ERROR] Profiles must be written directly under ${RUNTIME_CONFIG_DIR}." >&2
    return 2
  }
  [ ! -e "${output_path}" ] || {
    echo "[ERROR] Profile already exists: ${output_path}" >&2
    return 2
  }

  echo "[INFO] Profile v1 topology is fixed: single_gnb_rfsim, gNB=1, CU/DU split=0"
  read -r -p "Experiment name [${RUN_ID}]: " value
  PROFILE_NAME="${value:-${RUN_ID}}"
  read -r -p "Active UEs [${ACTIVE_UES}]: " value
  PROFILE_ACTIVE_UES="${value:-${ACTIVE_UES}}"
  read -r -p "PRB profile 51/106 [${N_RB_DL}]: " value
  PROFILE_N_RB_DL="${value:-${N_RB_DL}}"
  read -r -p "gNB config [${GNB_CONFIG}]: " value
  PROFILE_GNB_CONFIG="${value:-${GNB_CONFIG}}"
  read -r -p "CN compose [${CN_COMPOSE}]: " value
  PROFILE_CN_COMPOSE="${value:-${CN_COMPOSE}}"
  read -r -p "RedCap case case_a/case_b [${REDCAP_CASE}]: " value
  PROFILE_REDCAP_CASE="${value:-${REDCAP_CASE}}"
  read -r -p "Policy file [${POLICY_FILE}]: " value
  PROFILE_POLICY_FILE="${value:-${POLICY_FILE}}"
  read -r -p "Enable xApp 0/1 [${START_XAPP}]: " value
  PROFILE_START_XAPP="$(normalize_bool "${value:-${START_XAPP}}")"
  read -r -p "Enable dApp marker 0/1 [${DAPP_ENABLE}]: " value
  PROFILE_DAPP_ENABLE="$(normalize_bool "${value:-${DAPP_ENABLE}}")"

  PROFILE_VERSION_VALUE=${PROFILE_VERSION}
  PROFILE_TOPOLOGY=single_gnb_rfsim
  PROFILE_GNB_COUNT=1
  PROFILE_CU_DU_SPLIT=0
  PROFILE_TOTAL_UES=56
  PROFILE_CONTRACT_FILE=${CONTRACT_FILE}
  declare -gA PROFILE_SEEN=()
  local key
  for key in REDCAP_EXPERIMENT_PROFILE_VERSION REDCAP_EXPERIMENT_NAME REDCAP_TOPOLOGY REDCAP_GNB_COUNT REDCAP_CU_DU_SPLIT MMTC_TOTAL_UES MMTC_ACTIVE_UES MMTC_N_RB_DL GNB_REDCAP_CONFIG MMTC_CN_COMPOSE REDCAP_CASE REDCAP_POLICY_HOST_FILE REDCAP_CONTROL_CONTRACT_FILE MMTC_START_XAPP OAI_REDCAP_DAPP_GATE_D_MARKER; do
    PROFILE_SEEN[${key}]=1
  done
  validate_loaded_profile

  mkdir -p "$(dirname "${output_path}")"
  umask 077
  print_loaded_profile > "${output_path}"
  echo "[OK] Experiment profile created: ${output_path}"
  echo "[INFO] Review: redcap_interface/mmtc.menu.bash preview-profile ${output_path}"
  echo "[INFO] Run: redcap_interface/mmtc.menu.bash run-profile ${output_path} smoke"
}

apply_loaded_profile()
{
  RUN_ID=${PROFILE_NAME}
  GNB_CONFIG=${PROFILE_GNB_CONFIG}
  CN_COMPOSE=${PROFILE_CN_COMPOSE}
  ACTIVE_UES=${PROFILE_ACTIVE_UES}
  N_RB_DL=${PROFILE_N_RB_DL}
  REDCAP_CASE=${PROFILE_REDCAP_CASE}
  POLICY_FILE=${PROFILE_POLICY_FILE}
  CONTRACT_FILE=${PROFILE_CONTRACT_FILE}
  START_XAPP=${PROFILE_START_XAPP}
  DAPP_ENABLE=${PROFILE_DAPP_ENABLE}
  OVERLAY_COMPOSE="${RUNTIME_CONFIG_DIR}/${RUN_ID}_overlay.yml"
}

run_profile()
{
  local profile_path="$1"
  local mode="${2:-smoke}"
  load_profile "${profile_path}"
  apply_loaded_profile
  case "${mode}" in
    smoke) run_smoke ;;
    gate3) GATE1=1; GATE2=0; GATE3=1; GATE4=0; run_smoke ;;
    gate4) GATE1=1; GATE2=0; GATE3=1; GATE4=1; run_smoke ;;
    *)
      echo "[ERROR] Profile mode must be smoke, gate3, or gate4." >&2
      return 2
      ;;
  esac
}

check_inputs()
{
  require_file "${GNB_CONFIG}" "gNB config"
  require_file "${CN_COMPOSE}" "CN compose"
  require_file "${POLICY_FILE}" "policy file"
  require_file "${CONTRACT_FILE}" "control contract"
  require_file "${BASE_COMPOSE}" "base compose"
  require_file "${OVERLAY_GENERATOR}" "mMTC overlay generator"
}

ensure_overlay()
{
  validate_active_ues
  if [ ! -f "${OVERLAY_COMPOSE}" ]; then
    mkdir -p "${RUNTIME_CONFIG_DIR}"
    "${OVERLAY_GENERATOR}" "${TOTAL_UES}" "${OVERLAY_COMPOSE}"
  fi
}

show_mounts()
{
  check_inputs
  ensure_overlay
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
  read -r -p "Active UEs [${ACTIVE_UES}]: " value
  ACTIVE_UES="${value:-${ACTIVE_UES}}"
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
  ensure_overlay
  env \
    GNB_REDCAP_CONFIG="${GNB_CONFIG}" \
    MMTC_CN_COMPOSE="${CN_COMPOSE}" \
    MMTC_TOTAL_UES="${TOTAL_UES}" \
    MMTC_ACTIVE_UES="${ACTIVE_UES}" \
    MMTC_N_RB_DL="${N_RB_DL}" \
    MMTC_START_XAPP="${START_XAPP}" \
    OAI_REDCAP_DAPP_GATE_D_MARKER="${DAPP_ENABLE}" \
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
    MMTC_OVERLAY_COMPOSE="${OVERLAY_COMPOSE}" \
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
  ensure_overlay
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
    -h|--help) show_help ;;
    install)
      [ "$#" -le 2 ] || { echo "[ERROR] Use: install [--check|--help]" >&2; return 2; }
      shift
      bash "${INSTALLER}" "$@"
      ;;
    intro) show_intro ;;
    performance)
      if [ "${2:-}" = "reproduce" ]; then
        bash "${DISPLAY_MENU}"
      elif [ "$#" -eq 1 ]; then
        show_performance_evidence
      else
        echo "[ERROR] Use: performance [reproduce]" >&2
        return 2
      fi
      ;;
    experiment)
      [ "$#" -le 2 ] || { echo "[ERROR] Use: experiment [profile-path]" >&2; return 2; }
      create_experiment_profile "${2:-}"
      ;;
    preview-profile)
      [ "$#" -eq 2 ] || { echo "[ERROR] Use: preview-profile <path>" >&2; return 2; }
      preview_profile "$2"
      ;;
    run-profile)
      [ "$#" -ge 2 ] && [ "$#" -le 3 ] || { echo "[ERROR] Use: run-profile <path> [smoke|gate3|gate4]" >&2; return 2; }
      run_profile "$2" "${3:-smoke}"
      ;;
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
      echo "Use --help / 使用 --help 查看說明。" >&2
      return 2
      ;;
  esac
}

advanced_menu()
{
  local choice
  while true; do
    print_header
    cat <<'EOF'
1) Show mounted runtime files
2) Configure runtime paths / active UEs
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

main_menu()
{
  local choice
  while true; do
    cat <<EOF

RedCap Main Menu / 主選單
Repo: ${REPO_ROOT}

1) 安裝並執行 1 UE 驗收 / Install and run 1 UE acceptance
2) 開始專案介紹 / Project introduction
3) 展示已驗證效能 / Accepted performance evidence
4) 設定實驗 profile / Configure experiment profile
5) 進階 RFsim 操作 / Advanced RFsim operations
q) Quit
EOF
    read -r -p "Choice: " choice
    case "${choice}" in
      1) bash "${INSTALLER}"; pause_for_enter ;;
      2) show_intro; pause_for_enter ;;
      3)
        show_performance_evidence
        read -r -p "Open reproduction tools? 0/1 [0]: " choice
        [ "${choice:-0}" = "1" ] && bash "${DISPLAY_MENU}"
        ;;
      4) create_experiment_profile; pause_for_enter ;;
      5) advanced_menu ;;
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
