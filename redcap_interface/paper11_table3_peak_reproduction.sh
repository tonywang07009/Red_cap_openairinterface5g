#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/..")
PROJECT_ROOT="${REPO_ROOT}/agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1"

RUN_ID=${P11T3_RUN_ID:-paper11_table3_$(date +%F_%H-%M-%S)}
DURATION=${P11T3_DURATION:-60}
MAC_SAMPLE_DELAY=${P11T3_MAC_SAMPLE_DELAY:-8}
UE_INDEX=${P11T3_UE:-1}
UE_CONTAINER=${P11T3_UE_CONTAINER:-rfsim5g-oai-nr-ue${UE_INDEX}_redcap}
GNB_CONTAINER=${P11T3_GNB_CONTAINER:-rfsim5g-oai-gnb_redcap}
SERVER_CONTAINER=${P11T3_SERVER_CONTAINER:-oai-ext-dn}
BASE_PORT=${P11T3_BASE_PORT:-5231}
RAW_DIR=${P11T3_OUTPUT_DIR:-${PROJECT_ROOT}/analysis/data/paper11_table3_raw/${RUN_ID}}
CSV_PATH="${RAW_DIR}/${RUN_ID}_summary.csv"

GNB_CONFIG_51PRB="${REPO_ROOT}/ci-scripts/conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml"
GNB_CONFIG_106PRB="${REPO_ROOT}/ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml"

PROFILE=${P11T3_PROFILE:-51prb}
LIMITATION_NOTE="PAPER-11 Table 3 2.1G FDD target-rate proxy on stable RedCap RFsim; current run is not calibrated 2.1G FDD RF."

mkdir -p "${RAW_DIR}"

log()
{
  printf '[PAPER-11-T3][%s] %s\n' "$(date +%H:%M:%S)" "$*"
}

die()
{
  log "ERROR: $*"
  exit 1
}

profile_value()
{
  local key="$1"

  case "${PROFILE}:${key}" in
    51prb:gnb_config) printf '%s\n' "${GNB_CONFIG_51PRB}" ;;
    51prb:n_rb) printf '51\n' ;;
    51prb:rf_freq) printf '3617640000\n' ;;
    51prb:ssb_start) printf '238\n' ;;
    51prb:label) printf '51PRB_30k_TDD_proxy_for_20M_FDD\n' ;;
    106prb:gnb_config) printf '%s\n' "${GNB_CONFIG_106PRB}" ;;
    106prb:n_rb) printf '106\n' ;;
    106prb:rf_freq) printf '3630360000\n' ;;
    106prb:ssb_start) printf '144\n' ;;
    106prb:label) printf '106PRB_30k_TDD_stress_proxy\n' ;;
    *) die "unsupported P11T3_PROFILE=${PROFILE}; use 51prb or 106prb" ;;
  esac
}

docker_exec()
{
  docker exec "$@"
}

container_ipv4()
{
  local container="$1"
  local iface="$2"
  docker_exec "${container}" sh -c "ip -4 -o addr show dev ${iface} | sed -E 's/.*inet ([0-9.]+)\\/.*/\\1/' | head -n 1"
}

setup_profile()
{
  local pusch_256qam="$1"
  local pdsch_256qam="$2"
  local setup_id="$3"
  local setup_log="${RAW_DIR}/${RUN_ID}_${setup_id}_setup.log"

  log "Setting up profile=$(profile_value label), PUSCH256=${pusch_256qam}, PDSCH256=${pdsch_256qam}"
  (
    cd "${REPO_ROOT}"
    env \
      GNB_REDCAP_CONFIG="$(profile_value gnb_config)" \
      MMTC_N_RB_DL="$(profile_value n_rb)" \
      MMTC_RF_FREQ="$(profile_value rf_freq)" \
      MMTC_SSB_START="$(profile_value ssb_start)" \
      MMTC_TOTAL_UES=29 \
      MMTC_SAMPLE_UES="${UE_INDEX}" \
      MMTC_IPERF_SAMPLE_UES="${UE_INDEX}" \
      MMTC_IPERF_ENABLE=0 \
      MMTC_FORWARD_PING_MODE=parallel \
      MMTC_RUN_REVERSE_PING=0 \
      MMTC_PING_COUNT=5 \
      MMTC_GNB_WARMUP=5 \
      MMTC_SLEEP_AFTER_UP=25 \
      MMTC_UE_START_GAP=0 \
      MMTC_REDCAP_ENABLE=1 \
      MMTC_REDCAP_NUM_RX=1 \
      MMTC_REDCAP_HALF_DUPLEX=1 \
      MMTC_PUCCH_COMMON_FALLBACK_BWP0=1 \
      MMTC_PUSCH_256QAM="${pusch_256qam}" \
      MMTC_PDSCH_256QAM="${pdsch_256qam}" \
      bash redcap_interface/redcap_mmtc_smoke_validation.sh
  ) | tee "${setup_log}"

  docker_exec "${UE_CONTAINER}" sh -c 'cat /tmp/nr-ue-mmtc.yaml || true' > "${RAW_DIR}/${RUN_ID}_${setup_id}_ue_runtime_yaml.log" 2>&1 || true
  docker_exec "${GNB_CONTAINER}" sh -c "grep -nE 'dl_frequencyBand|dl_subcarrierSpacing|dl_carrierBandwidth|ul_frequencyBand|ul_subcarrierSpacing|ul_carrierBandwidth|nrofDownlinkSlots|nrofUplinkSlots|initialDLBWPSize_r17|initialULBWPSize_r17|bands:' /opt/oai-gnb/etc/gnb.yaml || true" \
    > "${RAW_DIR}/${RUN_ID}_${setup_id}_gnb_profile.log" 2>&1 || true
}

start_iperf_server()
{
  local port="$1"
  local log_path="$2"

  {
    echo "# collected_at=$(date --iso-8601=seconds)"
    echo "# server_container=${SERVER_CONTAINER}"
    echo "# port=${port}"
    docker_exec "${SERVER_CONTAINER}" sh -c "pids=\$(pidof iperf3 2>/dev/null || true); [ -z \"\$pids\" ] || kill \$pids; iperf3 -s -D -p ${port}"
  } > "${log_path}" 2>&1
}

capture_mac_stats()
{
  local direction="$1"
  local output_path="$2"
  local pattern

  if [ "${direction}" = "UL" ]; then
    pattern='ulsch_rounds|MCS|Qm|NPRB|SNR|CCE fail'
  else
    pattern='dlsch_rounds|MCS|BLER|CCE fail|pucch0_DTX'
  fi

  docker_exec "${GNB_CONTAINER}" sh -c "tail -n 180 /opt/oai-gnb/nrMAC_stats.log | grep -E '${pattern}' || true" \
    > "${output_path}" 2>&1 || true
}

rate_to_mbps()
{
  local rate="$1"
  awk -v rate="${rate}" 'BEGIN {
    value = rate
    unit = rate
    gsub(/[^0-9.].*/, "", value)
    gsub(/^[0-9.]+/, "", unit)
    unit = toupper(unit)
    if (unit ~ /^G/) printf "%.3f\n", value * 1000
    else if (unit ~ /^K/) printf "%.3f\n", value / 1000
    else printf "%.3f\n", value
  }'
}

parse_iperf()
{
  local log_path="$1"
  awk '
    function to_mbps(value, unit) {
      if (unit ~ /^Kbits/) return value / 1000.0
      if (unit ~ /^Mbits/) return value
      if (unit ~ /^Gbits/) return value * 1000.0
      return ""
    }
    / sender$/ {
      for (i = 1; i <= NF; i++) {
        if ($i ~ /bits\/sec$/ && i > 1) sender = to_mbps($(i - 1), $i)
      }
    }
    / receiver$/ {
      for (i = 1; i <= NF; i++) {
        if ($i ~ /bits\/sec$/ && i > 1) receiver = to_mbps($(i - 1), $i)
        if ($i == "ms" && i > 1) jitter = $(i - 1)
        if ($i ~ /^[0-9]+\/[0-9]+$/) {
          split($i, loss, "/")
          lost = loss[1]
          total = loss[2]
        }
        if ($i ~ /^\([0-9.]+%\)$/) {
          pct = $i
          gsub(/[()%]/, "", pct)
        }
      }
    }
    END {
      if (sender == "") sender = "NA"
      if (receiver == "") receiver = "NA"
      if (jitter == "") jitter = "NA"
      if (lost == "") lost = "NA"
      if (total == "") total = "NA"
      if (pct == "") pct = "NA"
      printf "%s,%s,%s,%s,%s,%s\n", sender, receiver, jitter, lost, total, pct
    }' "${log_path}"
}

write_csv_header()
{
  cat > "${CSV_PATH}" <<EOF
run_id,test_id,profile,paper_table,direction,modulation,pusch_256qam,pdsch_256qam,offered_rate_mbps,paper_target_mbps,sender_mbps,receiver_mbps,jitter_ms,lost_packets,total_packets,lost_percent,iperf_log,mac_log,status,limitation_note
EOF
}

append_csv_row()
{
  local test_id="$1"
  local direction="$2"
  local modulation="$3"
  local pusch_256qam="$4"
  local pdsch_256qam="$5"
  local offered_rate="$6"
  local paper_target="$7"
  local iperf_log="$8"
  local mac_log="$9"
  local parsed="${10}"
  local sender receiver jitter lost total pct status

  IFS=, read -r sender receiver jitter lost total pct <<< "${parsed}"
  status="PASS_WITH_GAP"
  if [ "${receiver}" = "NA" ]; then
    status="FAIL"
  else
    status=$(awk -v rx="${receiver}" -v target="${paper_target}" 'BEGIN { if (rx + 0 >= target + 0) print "PASS"; else print "PASS_WITH_GAP" }')
  fi

  printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"%s"\n' \
    "${RUN_ID}" \
    "${test_id}" \
    "$(profile_value label)" \
    "PAPER-11 Table 3 2.1G theoretical peak rate" \
    "${direction}" \
    "${modulation}" \
    "${pusch_256qam}" \
    "${pdsch_256qam}" \
    "$(rate_to_mbps "${offered_rate}")" \
    "${paper_target}" \
    "${sender}" \
    "${receiver}" \
    "${jitter}" \
    "${lost}" \
    "${total}" \
    "${pct}" \
    "${iperf_log}" \
    "${mac_log}" \
    "${status}" \
    "${LIMITATION_NOTE}" >> "${CSV_PATH}"
}

run_iperf_row()
{
  local test_id="$1"
  local direction="$2"
  local modulation="$3"
  local pusch_256qam="$4"
  local pdsch_256qam="$5"
  local offered_rate="$6"
  local paper_target="$7"
  local port="$8"
  local server_ip ue_ip iperf_log server_log mac_log reverse_arg

  server_ip=$(container_ipv4 "${SERVER_CONTAINER}" eth0)
  ue_ip=$(container_ipv4 "${UE_CONTAINER}" oaitun_ue1)
  [ -n "${server_ip}" ] || die "cannot resolve ${SERVER_CONTAINER} eth0 IP"
  [ -n "${ue_ip}" ] || die "cannot resolve ${UE_CONTAINER} oaitun_ue1 IP"

  iperf_log="${RAW_DIR}/${RUN_ID}_${test_id}_iperf.log"
  server_log="${RAW_DIR}/${RUN_ID}_${test_id}_server.log"
  mac_log="${RAW_DIR}/${RUN_ID}_${test_id}_mac.log"
  reverse_arg=()
  if [ "${direction}" = "DL" ]; then
    reverse_arg=(-R)
  fi

  log "Running ${test_id}: direction=${direction}, modulation=${modulation}, offered=${offered_rate}, target=${paper_target}Mbps"
  start_iperf_server "${port}" "${server_log}"

  set +e
  docker_exec "${UE_CONTAINER}" iperf3 \
    -c "${server_ip}" \
    -B "${ue_ip}" \
    -p "${port}" \
    -t "${DURATION}" \
    -i 1 \
    --forceflush \
    -u \
    -b "${offered_rate}" \
    "${reverse_arg[@]}" 2>&1 | tee "${iperf_log}" &
  local iperf_pid=$!
  sleep "${MAC_SAMPLE_DELAY}"
  capture_mac_stats "${direction}" "${mac_log}"
  wait "${iperf_pid}"
  set -e

  append_csv_row "${test_id}" "${direction}" "${modulation}" "${pusch_256qam}" "${pdsch_256qam}" "${offered_rate}" "${paper_target}" "${iperf_log}" "${mac_log}" "$(parse_iperf "${iperf_log}")"
  log "Stored ${test_id} logs: ${iperf_log}, ${mac_log}"
}

write_csv_header
log "Run ID: ${RUN_ID}"
log "Output directory: ${RAW_DIR}"
log "CSV summary: ${CSV_PATH}"
log "Duration: ${DURATION}s"
log "Profile: $(profile_value label)"

setup_profile 0 0 "64qam"
run_iperf_row "P11-T3-UL-64QAM-90M" "UL" "64QAM" 0 0 "90M" "90" "${BASE_PORT}"
run_iperf_row "P11-T3-DL-64QAM-169M5" "DL" "64QAM" 0 0 "169.5M" "169.5" "$((BASE_PORT + 1))"

setup_profile 0 1 "dl256qam"
run_iperf_row "P11-T3-DL-256QAM-226M" "DL" "256QAM" 0 1 "226M" "226" "$((BASE_PORT + 2))"

log "Completed PAPER-11 Table 3 target-rate proxy run"
log "CSV summary: ${CSV_PATH}"
