#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/..")

DEFAULT_GNB_CONFIG="${REPO_ROOT}/redcap_library/library_gnb_config/gnb_redcap_mmtc_case_b_final.yaml"
GNB_CONFIG_106PRB="${REPO_ROOT}/ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml"
GNB_CONFIG_51PRB="${REPO_ROOT}/ci-scripts/conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml"
DEFAULT_CN_COMPOSE="/home/tonywang/OAI/oai-cn5g/docker-compose.yaml"
BASE_COMPOSE="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml"
OVERLAY_COMPOSE="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml"
OVERLAY_GENERATOR="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh"
SMOKE_SCRIPT="${REPO_ROOT}/redcap_interface/redcap_mmtc_smoke_validation.sh"
PAPER11_SCRIPT="${REPO_ROOT}/redcap_interface/paper11_iperf_live_demo.sh"
PAPER11_TABLE3_SCRIPT="${REPO_ROOT}/redcap_interface/paper11_table3_peak_reproduction.sh"
IPERF_PANEL_SCRIPT="${REPO_ROOT}/redcap_interface/iperf_live_panel.py"
EVALUATION_RECOVER_DIR="${REPO_ROOT}/redcap_doc/evluation_recover"
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
N_RB_DL="${MMTC_N_RB_DL:-106}"
RF_FREQ="${MMTC_RF_FREQ:-3630360000}"
SSB_START="${MMTC_SSB_START:-144}"
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

infer_prb_profile()
{
  case "${GNB_CONFIG}" in
    *51PRB*)
      printf '51PRB full-carrier\n'
      ;;
    *106PRB*)
      printf '106PRB carrier\n'
      ;;
    *)
      printf 'custom\n'
      ;;
  esac
}

print_header()
{
  cat <<EOF

RedCap RFsim Runtime Menu
Repo           : ${REPO_ROOT}
gNB config     : ${GNB_CONFIG}
PRB profile    : $(infer_prb_profile)
UE -r PRB      : ${N_RB_DL}
UE RF freq     : ${RF_FREQ}
UE SSB start   : ${SSB_START}
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
  require_file "${OVERLAY_GENERATOR}" "mMTC overlay generator"
  require_file "${SMOKE_SCRIPT}" "smoke validation script"
}

compose_mount_check()
{
  check_inputs
  echo "[INFO] Checking final docker compose gNB mount"
  GNB_REDCAP_CONFIG="${GNB_CONFIG}" docker compose \
    --env-file /dev/null \
    -f "${BASE_COMPOSE}" \
    -f "${OVERLAY_COMPOSE}" \
    config | sed -n '/oai-gnb:/,/oai-nr-ue1:/p' | rg -n 'source:|target:|gnb.yaml' || true
  echo
  echo "[Expected]"
  echo "source: ${GNB_CONFIG}"
  echo "target: /opt/oai-gnb/etc/gnb.yaml"
  echo "MMTC_N_RB_DL: ${N_RB_DL}"
  echo "MMTC_RF_FREQ: ${RF_FREQ}"
  echo "MMTC_SSB_START: ${SSB_START}"
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
    MMTC_N_RB_DL="${N_RB_DL}" \
    MMTC_RF_FREQ="${RF_FREQ}" \
    MMTC_SSB_START="${SSB_START}" \
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

  read -r -p "UE -r PRB [${N_RB_DL}]: " value
  N_RB_DL="${value:-${N_RB_DL}}"

  read -r -p "UE RF frequency Hz [${RF_FREQ}]: " value
  RF_FREQ="${value:-${RF_FREQ}}"

  read -r -p "UE SSB start [${SSB_START}]: " value
  SSB_START="${value:-${SSB_START}}"

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

select_106prb_profile()
{
  GNB_CONFIG="${GNB_CONFIG_106PRB}"
  N_RB_DL=106
  RF_FREQ=3630360000
  SSB_START=144
  echo "[INFO] Selected 106PRB profile: gNB=${GNB_CONFIG}, UE -r=${N_RB_DL}, RF=${RF_FREQ}, ssb=${SSB_START}"
}

select_51prb_profile()
{
  GNB_CONFIG="${GNB_CONFIG_51PRB}"
  N_RB_DL=51
  RF_FREQ=3617640000
  SSB_START=238
  echo "[INFO] Selected full-carrier 51PRB profile: gNB=${GNB_CONFIG}, UE -r=${N_RB_DL}, RF=${RF_FREQ}, ssb=${SSB_START}"
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

run_paper07_reproduction_bundle()
{
  echo "[INFO] Running PAPER-07 reproduction bundle: 106PRB, UL 35M, DL 141M, PUSCH/PDSCH 256QAM"
  select_106prb_profile
  enable_paper07_256qam_profile
  run_smoke 1 "35M" "60"
  run_dl_iperf "141M" "60"
  echo "[INFO] PAPER-07 bundle finished"
  echo "[INFO] Step-by-step manual: ${EVALUATION_RECOVER_DIR}/paper07_tdd_reproduction_step_by_step.md"
}

run_paper11_reproduction_bundle()
{
  local duration="${P11_DURATION:-20}"
  local ul_rate="${P11_UL_RATE:-17M}"
  local dl_rate="${P11_DL_RATE:-68M}"

  if [ ! -x "${PAPER11_SCRIPT}" ]; then
    echo "[ERROR] Missing PAPER-11 script: ${PAPER11_SCRIPT}" >&2
    return 1
  fi

  echo "[INFO] Running PAPER-11 live reproduction with panel: UL=${ul_rate}, DL=${dl_rate}, duration=${duration}s"
  env \
    P11_PANEL=1 \
    P11_MODE=both \
    P11_UL_RATE="${ul_rate}" \
    P11_DL_RATE="${dl_rate}" \
    P11_DURATION="${duration}" \
    bash "${PAPER11_SCRIPT}"
  echo "[INFO] PAPER-11 bundle finished"
  echo "[INFO] Step-by-step manual: ${EVALUATION_RECOVER_DIR}/paper11_real_network_reproduction_step_by_step.md"
}

run_paper11_table3_bundle()
{
  local duration="${P11T3_DURATION:-60}"

  if [ ! -x "${PAPER11_TABLE3_SCRIPT}" ]; then
    echo "[ERROR] Missing PAPER-11 Table 3 script: ${PAPER11_TABLE3_SCRIPT}" >&2
    return 1
  fi

  echo "[INFO] Running PAPER-11 Table 3 RedCap target-rate proxy, duration=${duration}s"
  env \
    P11T3_PROFILE="${P11T3_PROFILE:-51prb}" \
    P11T3_DURATION="${duration}" \
    bash "${PAPER11_TABLE3_SCRIPT}"
  echo "[INFO] PAPER-11 Table 3 bundle finished"
  echo "[INFO] Step-by-step manual: ${EVALUATION_RECOVER_DIR}/paper11_table3_2p1g_peak_rate_step_by_step.md"
}

run_standalone_iperf_panel()
{
  local direction="${PANEL_DIRECTION:-both}"
  local ul_rate="${PANEL_UL_RATE:-${IPERF_RATE}}"
  local dl_rate="${PANEL_DL_RATE:-${DL_IPERF_RATE}}"
  local duration="${PANEL_DURATION:-20}"

  if [ ! -x "${IPERF_PANEL_SCRIPT}" ]; then
    echo "[ERROR] Missing iperf panel script: ${IPERF_PANEL_SCRIPT}" >&2
    return 1
  fi

  read -r -p "Direction ul/dl/both [${direction}]: " direction
  direction="${direction:-${PANEL_DIRECTION:-both}}"
  read -r -p "UL rate [${ul_rate}]: " ul_rate
  ul_rate="$(normalize_iperf_rate "${ul_rate:-${PANEL_UL_RATE:-${IPERF_RATE}}}")"
  read -r -p "DL rate [${dl_rate}]: " dl_rate
  dl_rate="$(normalize_iperf_rate "${dl_rate:-${PANEL_DL_RATE:-${DL_IPERF_RATE}}}")"
  read -r -p "Duration seconds [${duration}]: " duration
  duration="${duration:-${PANEL_DURATION:-20}}"

  python3 "${IPERF_PANEL_SCRIPT}" \
    --direction "${direction}" \
    --ue 1 \
    --protocol udp \
    --ul-rate "${ul_rate}" \
    --dl-rate "${dl_rate}" \
    --duration "${duration}"
}

show_evaluation_recover_docs()
{
  echo "[INFO] Evaluation reproduction manuals: ${EVALUATION_RECOVER_DIR}"
  if [ ! -d "${EVALUATION_RECOVER_DIR}" ]; then
    echo "[WARN] Directory does not exist"
    return 0
  fi
  find "${EVALUATION_RECOVER_DIR}" -maxdepth 1 -type f -name '*.md' -printf '%f\n' | sort
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

probe_compose()
{
  local override_file="$1"
  shift

  env \
    GNB_REDCAP_CONFIG="${GNB_CONFIG}" \
    MMTC_N_RB_DL="${N_RB_DL}" \
    MMTC_RF_FREQ="${RF_FREQ}" \
    MMTC_SSB_START="${SSB_START}" \
    MMTC_PUSCH_256QAM="${PUSCH_256QAM}" \
    MMTC_PDSCH_256QAM="${PDSCH_256QAM}" \
    MMTC_PUCCH_COMMON_FALLBACK_BWP0=1 \
    docker compose \
      --env-file /dev/null \
      -f "${BASE_COMPOSE}" \
      -f "${OVERLAY_COMPOSE}" \
      -f "${override_file}" \
      "$@"
}

write_redcap_vs_normal_override()
{
  local override_file="$1"

  cat > "${override_file}" <<EOF
services:
  oai-gnb:
    image: oai-gnb:latest
  oai-nr-ue1:
    image: oai-nr-ue:latest
    environment:
      MMTC_EXPERIMENT_ROLE: "normal-probe"
      MMTC_REDCAP_ENABLE: "0"
      MMTC_REDCAP_HALF_DUPLEX: "0"
      MMTC_TEMPLATE_CONFIG: /opt/oai-nr-ue/etc/nr-ue.yaml
    volumes:
      - ${REPO_ROOT}/ci-scripts/conf_files/nrue/nrue1.uicc.yaml:/opt/oai-nr-ue/etc/nr-ue.yaml:ro
      - ${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/ue_mmtc_entrypoint.sh:/opt/oai-nr-ue/bin/entrypoint.sh:ro
  oai-nr-ue2:
    image: oai-nr-ue:latest
    environment:
      MMTC_EXPERIMENT_ROLE: "redcap-probe"
      MMTC_REDCAP_ENABLE: "1"
      MMTC_REDCAP_NUM_RX: "1"
      MMTC_REDCAP_HALF_DUPLEX: "1"
EOF
}

container_status_or_dash()
{
  local container="$1"

  docker inspect -f '{{.State.Status}}' "${container}" 2>/dev/null || printf -- '-'
}

ue_tun_ipv4_or_dash()
{
  local container="$1"

  docker exec "${container}" sh -c "ip -4 -o addr show 2>/dev/null | awk '\$2 ~ /^oaitun/ { split(\$4, a, \"/\"); print a[1]; exit }'" \
    2>/dev/null || printf -- '-'
}

ue_log_has()
{
  local container="$1"
  local pattern="$2"
  local logs

  logs="$(docker logs "${container}" 2>&1 || true)"
  rg -q "${pattern}" <<< "${logs}"
}

ue_log_first_or_dash()
{
  local container="$1"
  local pattern="$2"
  local logs
  local line

  logs="$(docker logs "${container}" 2>&1 || true)"
  line="$(rg -m1 "${pattern}" <<< "${logs}" || true)"
  if [ -z "${line}" ]; then
    printf -- '-'
  else
    printf '%s' "${line}"
  fi
}

print_probe_row()
{
  local ue_label="$1"
  local container="$2"
  local expected_redcap="$3"
  local status
  local tun_ip
  local config_marker
  local cap_marker="no"
  local registration="no"
  local pdu="no"
  local verdict="WAIT"
  local config_matches="0"

  status="$(container_status_or_dash "${container}")"
  tun_ip="$(ue_tun_ipv4_or_dash "${container}")"
  [ -n "${tun_ip}" ] || tun_ip="-"
  config_marker="$(ue_log_first_or_dash "${container}" 'nrue_recap RedCap config:.*RedCap=[01]|support_of_redcap_r17:[[:space:]]*[01]')"

  if [ "${expected_redcap}" = "0" ] && [ "${config_marker}" = "-" ]; then
    config_marker="no-nrue-recap"
  fi

  if ue_log_has "${container}" 'Built RedCap UE capability: supportOfRedCap-r17=1|Using RedCap UE capability for UECapabilityInformation: supportOfRedCap-r17=1|Built UE NR capability from nrue_recap YAML'; then
    cap_marker="yes"
  fi
  if [ "${expected_redcap}" = "1" ] && ue_log_has "rfsim5g-oai-gnb_redcap" 'UE with RNTI [0-9a-fA-F]{4} is RedCap'; then
    cap_marker="yes"
  fi
  if ue_log_has "${container}" 'Registration Accept|REGISTRATION ACCEPT|5GMM.*REGISTERED|registration.*accepted'; then
    registration="yes"
  fi
  if ue_log_has "${container}" 'PDU Session Establishment Accept|PDU Session.*accept|oaitun'; then
    pdu="yes"
  fi
  if [ "${tun_ip}" != "-" ]; then
    registration="yes"
    pdu="yes"
  fi

  if [ "${expected_redcap}" = "1" ] \
    && { [[ "${config_marker}" == *"RedCap=1"* ]] || [[ "${config_marker}" == *"support_of_redcap_r17: 1"* ]]; }; then
    config_matches="1"
  elif [ "${expected_redcap}" = "0" ] \
    && { [[ "${config_marker}" == *"RedCap=0"* ]] \
      || [[ "${config_marker}" == *"support_of_redcap_r17: 0"* ]] \
      || [[ "${config_marker}" == *"no-nrue-recap"* ]]; } \
    && [ "${cap_marker}" = "no" ]; then
    config_matches="1"
  fi

  if [ "${status}" = "running" ] && [ "${tun_ip}" != "-" ] && [ "${config_matches}" = "1" ]; then
    if [ "${expected_redcap}" = "1" ] && [ "${cap_marker}" = "no" ]; then
      verdict="FLOW"
    else
      verdict="PASS"
    fi
  fi

  printf '%-8s %-12s %-10s %-16s %-8s %-12s %-5s %-4s %-4s %s\n' \
    "$(date +%H:%M:%S)" "${ue_label}" "${status}" "${tun_ip}" "RC=${expected_redcap}" \
    "cap=${cap_marker}" "${registration}" "${pdu}" "${verdict}" "${config_marker}"
}

run_redcap_vs_nonredcap_probe()
{
  local timestamp
  local override_file
  local log_file
  local rounds
  local interval
  local gnb_warmup

  check_inputs
  mkdir -p "${LOG_DIR}"

  timestamp="$(date +%F_%H-%M-%S)"
  override_file="${LOG_DIR}/redcap_vs_nonredcap_${timestamp}_override.yml"
  log_file="${LOG_DIR}/redcap_vs_nonredcap_${timestamp}_live.log"
  rounds="${REDCAP_VS_NORMAL_WATCH_ROUNDS:-18}"
  interval="${REDCAP_VS_NORMAL_WATCH_INTERVAL:-5}"
  gnb_warmup="${REDCAP_VS_NORMAL_GNB_WARMUP:-18}"

  write_redcap_vs_normal_override "${override_file}"

  {
    echo "[INFO] RedCap vs non-RedCap live probe"
    echo "[INFO] Log file: ${log_file}"
    echo "[INFO] Override compose: ${override_file}"
    echo "[INFO] Logic: UE1 normal UE path, UE2 RedCap path; same gNB/CN/RF/PRB profile"
    echo "[INFO] Profile: gNB=${GNB_CONFIG}, UE -r=${N_RB_DL}, RF=${RF_FREQ}, ssb=${SSB_START}, PUCCH_BWP0=1, PUSCH256=${PUSCH_256QAM}, PDSCH256=${PDSCH_256QAM}"
    echo
    echo "[INFO] Generating mMTC overlay for UE1..UE${TOTAL_UES}"
    "${OVERLAY_GENERATOR}" "${TOTAL_UES}" "${OVERLAY_COMPOSE}"

    echo "[INFO] Starting CN compose"
    docker compose --env-file /dev/null -f "${CN_COMPOSE}" up -d

    echo "[INFO] Resetting OAI RedCap RFsim compose"
    probe_compose "${override_file}" down --remove-orphans

    echo "[INFO] Starting nearRT-RIC and gNB"
    probe_compose "${override_file}" up -d nearRT-RIC oai-gnb
    sleep "${gnb_warmup}"

    echo "[INFO] Starting UE1 as non-RedCap"
    probe_compose "${override_file}" up -d oai-nr-ue1
    sleep "${REDCAP_VS_NORMAL_UE_GAP:-8}"

    echo "[INFO] Starting UE2 as RedCap"
    probe_compose "${override_file}" up -d oai-nr-ue2
    echo
    printf '%-8s %-12s %-10s %-16s %-8s %-12s %-5s %-4s %-4s %s\n' \
      "time" "ue" "container" "tun_ip" "expect" "capability" "reg" "pdu" "ok" "config_marker"

    for ((round=1; round<=rounds; round++)); do
      print_probe_row "UE1-Normal" "rfsim5g-oai-nr-ue1_redcap" "0"
      print_probe_row "UE2-RedCap" "rfsim5g-oai-nr-ue2_redcap" "1"
      sleep "${interval}"
    done

    echo
    echo "[INFO] Decision rule"
    echo "- UE1 expected: runtime YAML RedCap=0 and UE capability log does not contain supportOfRedCap-r17."
    echo "- UE2 expected: runtime YAML RedCap=1 and UE capability log contains supportOfRedCap-r17."
    echo "- ok=FLOW means the expected runtime YAML path and TUN IP are present, but the capability marker was not found."
    echo "- ok=PASS means the expected runtime path, TUN IP, and capability marker expectation all match."
    echo "- Both should reach running container state and oaitun IPv4 under the same gNB/CN profile."
  } 2>&1 | tee "${log_file}"
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
 13) Select 106PRB carrier profile
 14) Select 51PRB full-carrier profile
 15) Run RedCap vs non-RedCap live probe
  16) Run PAPER-07 reproduction bundle
  17) Run PAPER-11 reproduction with live iperf panel
  18) Run standalone iperf live panel
  19) Show evaluation recovery manuals
  20) Run PAPER-11 Table 3 RedCap peak-rate proxy
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
      13) select_106prb_profile; pause_for_enter ;;
      14) select_51prb_profile; pause_for_enter ;;
      15) run_redcap_vs_nonredcap_probe; pause_for_enter ;;
      16) run_paper07_reproduction_bundle; pause_for_enter ;;
      17) run_paper11_reproduction_bundle; pause_for_enter ;;
      18) run_standalone_iperf_panel; pause_for_enter ;;
      19) show_evaluation_recover_docs; pause_for_enter ;;
      20) run_paper11_table3_bundle; pause_for_enter ;;
      q|Q) exit 0 ;;
      *) echo "[WARN] Unknown choice: ${choice}"; pause_for_enter ;;
    esac
  done
}

if [ "${1:-}" = "redcap-vs-normal" ]; then
  run_redcap_vs_nonredcap_probe
  exit $?
fi

main_menu "$@"
