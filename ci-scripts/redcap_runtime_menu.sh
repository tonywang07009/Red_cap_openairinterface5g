#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/..")

DEFAULT_GNB_CONFIG="${REPO_ROOT}/test_log/runtime_configs/gnb.redcap_mmtc_case-b_2026-05-02_12-35-01.yaml"
DEFAULT_CN_COMPOSE="/home/tonywang/OAI/oai-cn5g/docker-compose.yaml"
BASE_COMPOSE="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml"
OVERLAY_COMPOSE="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml"
SMOKE_SCRIPT="${REPO_ROOT}/ci-scripts/redcap_mmtc_smoke_validation.sh"
LOG_DIR="${REPO_ROOT}/test_log/compiler_logs"

GNB_CONFIG="${GNB_REDCAP_CONFIG:-${DEFAULT_GNB_CONFIG}}"
CN_COMPOSE="${MMTC_CN_COMPOSE:-${DEFAULT_CN_COMPOSE}}"
TOTAL_UES="${MMTC_TOTAL_UES:-29}"
SAMPLE_UES="${MMTC_SAMPLE_UES:-1}"
IPERF_SAMPLE_UES="${MMTC_IPERF_SAMPLE_UES:-${SAMPLE_UES}}"
IPERF_RATE="${MMTC_IPERF_RATE:-85M}"
IPERF_DURATION="${MMTC_IPERF_DURATION:-30}"

print_header()
{
  cat <<EOF

RedCap RFsim Runtime Menu
Repo           : ${REPO_ROOT}
gNB config     : ${GNB_CONFIG}
CN compose     : ${CN_COMPOSE}
Total UEs      : ${TOTAL_UES}
Sample UEs     : ${SAMPLE_UES}
iperf UEs      : ${IPERF_SAMPLE_UES}
iperf rate     : ${IPERF_RATE}
iperf duration : ${IPERF_DURATION}s

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
  require_file "${BASE_COMPOSE}" "base compose"
  require_file "${OVERLAY_COMPOSE}" "mMTC overlay compose"
  require_file "${SMOKE_SCRIPT}" "smoke validation script"
}

compose_mount_check()
{
  check_inputs
  echo "[INFO] Checking final docker compose gNB mount"
  GNB_REDCAP_CONFIG="${GNB_CONFIG}" docker compose \
    -f "${BASE_COMPOSE}" \
    -f "${OVERLAY_COMPOSE}" \
    config | sed -n '/oai-gnb:/,/oai-nr-ue1:/p' | rg -n 'source:|target:|gnb.yaml' || true
  echo
  echo "[Expected]"
  echo "source: ${GNB_CONFIG}"
  echo "target: /opt/oai-gnb/etc/gnb.yaml"
}

run_smoke()
{
  local iperf_enable="$1"
  local rate="$2"
  local duration="$3"

  check_inputs
  echo "[INFO] Running RedCap smoke validation: iperf=${iperf_enable}, rate=${rate}, duration=${duration}s"
  env \
    GNB_REDCAP_CONFIG="${GNB_CONFIG}" \
    MMTC_TOTAL_UES="${TOTAL_UES}" \
    MMTC_SAMPLE_UES="${SAMPLE_UES}" \
    MMTC_IPERF_SAMPLE_UES="${IPERF_SAMPLE_UES}" \
    MMTC_CN_COMPOSE="${CN_COMPOSE}" \
    MMTC_USE_EXISTING_CN_DB=1 \
    MMTC_UE_START_GAP=8 \
    MMTC_FORWARD_PING_MODE=parallel \
    MMTC_RUN_REVERSE_PING=0 \
    MMTC_IPERF_ENABLE="${iperf_enable}" \
    MMTC_IPERF_UDP=1 \
    MMTC_IPERF_RATE="${rate}" \
    MMTC_IPERF_DURATION="${duration}" \
    MMTC_PUCCH_COMMON_FALLBACK_BWP0=1 \
    bash "${SMOKE_SCRIPT}"
}

show_latest_iperf_log()
{
  local latest_log

  latest_log=$(ls -t "${LOG_DIR}"/mmtc_smoke_*_ue1_iperf3_ul.log 2>/dev/null | head -n 1 || true)
  if [ -z "${latest_log}" ]; then
    echo "[WARN] No UE1 iperf3 UL log found under ${LOG_DIR}"
    return 0
  fi

  echo "[INFO] Latest iperf log: ${latest_log}"
  tail -n 40 "${latest_log}"
  echo
  echo "[INFO] Key throughput lines"
  rg -n "sender|receiver|Mbits/sec|Gbits/sec|lost|%" "${latest_log}" || true
}

configure_values()
{
  local value

  read -r -p "gNB config [${GNB_CONFIG}]: " value
  GNB_CONFIG="${value:-${GNB_CONFIG}}"

  read -r -p "CN compose [${CN_COMPOSE}]: " value
  CN_COMPOSE="${value:-${CN_COMPOSE}}"

  read -r -p "Total UEs [${TOTAL_UES}]: " value
  TOTAL_UES="${value:-${TOTAL_UES}}"

  read -r -p "Sample UEs, numbers only [${SAMPLE_UES}]: " value
  SAMPLE_UES="${value:-${SAMPLE_UES}}"

  read -r -p "iperf sample UEs [${IPERF_SAMPLE_UES}]: " value
  IPERF_SAMPLE_UES="${value:-${IPERF_SAMPLE_UES}}"

  read -r -p "iperf rate [${IPERF_RATE}]: " value
  IPERF_RATE="${value:-${IPERF_RATE}}"

  read -r -p "iperf duration seconds [${IPERF_DURATION}]: " value
  IPERF_DURATION="${value:-${IPERF_DURATION}}"
}

custom_iperf_run()
{
  local rate="${IPERF_RATE}"
  local duration="${IPERF_DURATION}"

  read -r -p "UDP uplink rate, e.g. 85M/100M [${rate}]: " rate
  rate="${rate:-${IPERF_RATE}}"
  read -r -p "Duration seconds [${duration}]: " duration
  duration="${duration:-${IPERF_DURATION}}"
  run_smoke 1 "${rate}" "${duration}"
}

main_menu()
{
  local choice

  while true; do
    print_header
    cat <<EOF
Select action:
  1) Check gNB config mount
  2) Run single-sample baseline, no iperf
  3) Run UDP uplink iperf with current rate
  4) Run UDP uplink iperf with custom rate
  5) Show latest UE1 iperf log
  6) Configure paths and UE/rate values
  q) Quit

EOF
    read -r -p "Choice: " choice
    case "${choice}" in
      1) compose_mount_check; pause_for_enter ;;
      2) run_smoke 0 "${IPERF_RATE}" "${IPERF_DURATION}"; pause_for_enter ;;
      3) run_smoke 1 "${IPERF_RATE}" "${IPERF_DURATION}"; pause_for_enter ;;
      4) custom_iperf_run; pause_for_enter ;;
      5) show_latest_iperf_log; pause_for_enter ;;
      6) configure_values ;;
      q|Q) exit 0 ;;
      *) echo "[WARN] Unknown choice: ${choice}"; pause_for_enter ;;
    esac
  done
}

main_menu "$@"
