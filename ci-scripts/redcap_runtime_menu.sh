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

normalize_iperf_rate()
{
  local rate="$1"

  if [[ "${rate}" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
    printf '%sM\n' "${rate}"
  else
    printf '%s\n' "${rate}"
  fi
}

normalize_bool()
{
  local value="$1"

  case "${value,,}" in
    1|true|t|yes|y|on|enable|enabled)
      printf '1\n'
      ;;
    0|false|f|no|n|off|disable|disabled)
      printf '0\n'
      ;;
    *)
      echo "[WARN] Invalid boolean value '${value}', using 0" >&2
      printf '0\n'
      ;;
  esac
}

GNB_CONFIG="${GNB_REDCAP_CONFIG:-${DEFAULT_GNB_CONFIG}}"
CN_COMPOSE="${MMTC_CN_COMPOSE:-${DEFAULT_CN_COMPOSE}}"
TOTAL_UES="${MMTC_TOTAL_UES:-29}"
SAMPLE_UES="${MMTC_SAMPLE_UES:-1}"
IPERF_SAMPLE_UES="${MMTC_IPERF_SAMPLE_UES:-${SAMPLE_UES}}"
IPERF_RATE="$(normalize_iperf_rate "${MMTC_IPERF_RATE:-85M}")"
IPERF_DURATION="${MMTC_IPERF_DURATION:-30}"
DL_IPERF_SERVER_IP="${MMTC_DL_IPERF_SERVER_IP:-${MMTC_IPERF_SERVER_IP:-192.168.72.135}}"
DL_IPERF_RATE="$(normalize_iperf_rate "${MMTC_DL_IPERF_RATE:-141M}")"
DL_IPERF_DURATION="${MMTC_DL_IPERF_DURATION:-60}"
PUSCH_256QAM="$(normalize_bool "${MMTC_PUSCH_256QAM:-0}")"
PDSCH_256QAM="$(normalize_bool "${MMTC_PDSCH_256QAM:-0}")"

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
DL server IP   : ${DL_IPERF_SERVER_IP}
DL iperf rate  : ${DL_IPERF_RATE}
DL duration    : ${DL_IPERF_DURATION}s
PUSCH 256QAM   : ${PUSCH_256QAM}
PDSCH 256QAM   : ${PDSCH_256QAM}

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
  local normalized_rate

  normalized_rate="$(normalize_iperf_rate "${rate}")"
  if [ "${normalized_rate}" != "${rate}" ]; then
    echo "[INFO] Normalized unitless iperf rate '${rate}' to '${normalized_rate}'"
  fi

  check_inputs
  echo "[INFO] Running RedCap smoke validation: iperf=${iperf_enable}, rate=${normalized_rate}, duration=${duration}s, PUSCH256QAM=${PUSCH_256QAM}, PDSCH256QAM=${PDSCH_256QAM}"
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
    MMTC_IPERF_RATE="${normalized_rate}" \
    MMTC_IPERF_DURATION="${duration}" \
    MMTC_PUCCH_COMMON_FALLBACK_BWP0=1 \
    MMTC_PUSCH_256QAM="${PUSCH_256QAM}" \
    MMTC_PDSCH_256QAM="${PDSCH_256QAM}" \
    bash "${SMOKE_SCRIPT}"
}

show_latest_iperf_log()
{
  local latest_log

  latest_log=$(ls -t \
    "${LOG_DIR}"/mmtc_smoke_*_ue1_iperf3_ul.log \
    "${LOG_DIR}"/redcap_menu_*_ue1_iperf3_dl.log \
    2>/dev/null | head -n 1 || true)
  if [ -z "${latest_log}" ]; then
    echo "[WARN] No UE1 iperf3 UL/DL log found under ${LOG_DIR}"
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
  IPERF_RATE="$(normalize_iperf_rate "${value:-${IPERF_RATE}}")"

  read -r -p "iperf duration seconds [${IPERF_DURATION}]: " value
  IPERF_DURATION="${value:-${IPERF_DURATION}}"

  read -r -p "DL iperf server IP [${DL_IPERF_SERVER_IP}]: " value
  DL_IPERF_SERVER_IP="${value:-${DL_IPERF_SERVER_IP}}"

  read -r -p "DL iperf rate [${DL_IPERF_RATE}]: " value
  DL_IPERF_RATE="$(normalize_iperf_rate "${value:-${DL_IPERF_RATE}}")"

  read -r -p "DL iperf duration seconds [${DL_IPERF_DURATION}]: " value
  DL_IPERF_DURATION="${value:-${DL_IPERF_DURATION}}"
}

configure_256qam()
{
  local value

  read -r -p "Enable UL/PUSCH 256QAM? 0/1 [${PUSCH_256QAM}]: " value
  PUSCH_256QAM="$(normalize_bool "${value:-${PUSCH_256QAM}}")"

  read -r -p "Enable DL/PDSCH 256QAM? 0/1 [${PDSCH_256QAM}]: " value
  PDSCH_256QAM="$(normalize_bool "${value:-${PDSCH_256QAM}}")"
}

enable_paper07_256qam_profile()
{
  PUSCH_256QAM=1
  PDSCH_256QAM=1
  IPERF_RATE="35M"
  IPERF_DURATION=60
  DL_IPERF_RATE="141M"
  DL_IPERF_DURATION=60

  echo "[INFO] Enabled PAPER-07 256QAM profile: PUSCH256QAM=1, PDSCH256QAM=1, UL rate=35M, DL rate=141M, duration=60s"
  echo "[INFO] Run option 2 or 3 to restart/apply UE capability before running DL iperf"
}

enable_paper07_dl_64qam_profile()
{
  PDSCH_256QAM=0
  DL_IPERF_RATE="106M"
  DL_IPERF_DURATION=60

  echo "[INFO] Enabled PAPER-07 DL 64QAM-level profile: PDSCH256QAM=0, DL rate=106M, duration=60s"
  echo "[INFO] Run option 2 or 3 to restart/apply UE capability before running DL iperf"
}

enable_paper07_dl_256qam_profile()
{
  PDSCH_256QAM=1
  DL_IPERF_RATE="141M"
  DL_IPERF_DURATION=60

  echo "[INFO] Enabled PAPER-07 DL 256QAM profile: PDSCH256QAM=1, DL rate=141M, duration=60s"
  echo "[INFO] Run option 2 or 3 to restart/apply UE capability before running DL iperf"
}

custom_iperf_run()
{
  local rate="${IPERF_RATE}"
  local duration="${IPERF_DURATION}"

  read -r -p "UDP uplink rate, e.g. 85M/100M [${rate}]: " rate
  rate="$(normalize_iperf_rate "${rate:-${IPERF_RATE}}")"
  read -r -p "Duration seconds [${duration}]: " duration
  duration="${duration:-${IPERF_DURATION}}"
  run_smoke 1 "${rate}" "${duration}"
}

extract_ue_tun_ipv4()
{
  docker exec rfsim5g-oai-nr-ue1_redcap sh -c "ip -4 -o addr show dev oaitun_ue1 | sed -n 's/.*inet \([0-9.]*\)\/.*/\1/p' | head -n 1"
}

start_iperf_server()
{
  echo "[INFO] Starting ext-dn iperf3 server"
  docker exec oai-ext-dn sh -c 'pids=$(pidof iperf3 2>/dev/null || true); [ -z "$pids" ] || kill $pids; iperf3 -s -D'
}

run_dl_iperf()
{
  local rate="$1"
  local duration="$2"
  local normalized_rate
  local timestamp
  local log_file
  local ue_ipv4

  normalized_rate="$(normalize_iperf_rate "${rate}")"
  if [ "${normalized_rate}" != "${rate}" ]; then
    echo "[INFO] Normalized unitless DL iperf rate '${rate}' to '${normalized_rate}'"
  fi

  mkdir -p "${LOG_DIR}"
  ue_ipv4="$(extract_ue_tun_ipv4)"
  if [ -z "${ue_ipv4}" ]; then
    echo "[ERROR] Could not resolve UE1 oaitun_ue1 IPv4 address" >&2
    return 1
  fi

  start_iperf_server

  timestamp="$(date +%F_%H-%M-%S)"
  log_file="${LOG_DIR}/redcap_menu_${timestamp}_ue1_iperf3_dl.log"
  echo "[INFO] DL iperf3 oai-ext-dn -> rfsim5g-oai-nr-ue1_redcap (UE IPv4=${ue_ipv4}, server=${DL_IPERF_SERVER_IP}, rate=${normalized_rate}, duration=${duration}s, PDSCH256QAM=${PDSCH_256QAM})"
  {
    echo "# collected_at=$(date --iso-8601=seconds)"
    echo "# direction=DL"
    echo "# ue=1"
    echo "# container=rfsim5g-oai-nr-ue1_redcap"
    echo "# target=${DL_IPERF_SERVER_IP}"
    echo "# ue_ipv4=${ue_ipv4}"
    echo "# pdsch_256qam=${PDSCH_256QAM}"
    echo "# command: docker exec rfsim5g-oai-nr-ue1_redcap iperf3 -c ${DL_IPERF_SERVER_IP} -B ${ue_ipv4} -t ${duration} -u -b ${normalized_rate} -R"
    docker exec rfsim5g-oai-nr-ue1_redcap iperf3 -c "${DL_IPERF_SERVER_IP}" -B "${ue_ipv4}" -t "${duration}" -u -b "${normalized_rate}" -R
  } | tee "${log_file}"

  echo "[INFO] DL iperf log: ${log_file}"
  echo "[INFO] Key throughput lines"
  rg -n "sender|receiver|Mbits/sec|Gbits/sec|lost|%" "${log_file}" || true
}

custom_dl_iperf_run()
{
  local rate="${DL_IPERF_RATE}"
  local duration="${DL_IPERF_DURATION}"

  read -r -p "UDP downlink rate, e.g. 106M/141M [${rate}]: " rate
  rate="$(normalize_iperf_rate "${rate:-${DL_IPERF_RATE}}")"
  read -r -p "Duration seconds [${duration}]: " duration
  duration="${duration:-${DL_IPERF_DURATION}}"
  run_dl_iperf "${rate}" "${duration}"
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
  7) Configure 256QAM capability
  8) Enable PAPER-07 256QAM profile
  9) Enable PAPER-07 DL 64QAM profile
 10) Enable PAPER-07 DL 256QAM profile
 11) Run UDP downlink iperf with current DL rate
 12) Run UDP downlink iperf with custom DL rate
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
      7) configure_256qam ;;
      8) enable_paper07_256qam_profile; pause_for_enter ;;
      9) enable_paper07_dl_64qam_profile; pause_for_enter ;;
      10) enable_paper07_dl_256qam_profile; pause_for_enter ;;
      11) run_dl_iperf "${DL_IPERF_RATE}" "${DL_IPERF_DURATION}"; pause_for_enter ;;
      12) custom_dl_iperf_run; pause_for_enter ;;
      q|Q) exit 0 ;;
      *) echo "[WARN] Unknown choice: ${choice}"; pause_for_enter ;;
    esac
  done
}

main_menu "$@"
