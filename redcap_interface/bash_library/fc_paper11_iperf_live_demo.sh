#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
INTERFACE_DIR=$(realpath "${SCRIPT_DIR}/..")
REPO_ROOT=$(realpath "${INTERFACE_DIR}/..")
PROJECT_ROOT="${REPO_ROOT}/agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1"
RUN_ID=${P11_RUN_ID:-paper11_live_iperf_$(date +%F_%H-%M-%S)}
UE_INDEX=${P11_UE:-1}
MODE=${P11_MODE:-both}
PROTOCOL=${P11_PROTOCOL:-udp}
UL_RATE=${P11_UL_RATE:-17M}
DL_RATE=${P11_DL_RATE:-68M}
DURATION=${P11_DURATION:-20}
PING_COUNT=${P11_PING_COUNT:-10}
BASE_PORT=${P11_BASE_PORT:-5211}
SETUP=${P11_SETUP:-0}
SERVER_CONTAINER=${P11_SERVER_CONTAINER:-oai-ext-dn}
UE_CONTAINER=${P11_UE_CONTAINER:-rfsim5g-oai-nr-ue${UE_INDEX}_redcap}
RAW_DIR=${P11_OUTPUT_DIR:-${PROJECT_ROOT}/analysis/data/paper11_live_iperf_raw/${RUN_ID}}
CSV_PATH="${RAW_DIR}/${RUN_ID}_summary.csv"
PANEL=${P11_PANEL:-0}
PANEL_SCRIPT="${REPO_ROOT}/redcap_interface/iperf_live_panel.py"
LIMITATION_NOTE="RFsim/OAI-CN/OAI-nrUE proxy; not commercial-network RF, physical coverage, or UE current measurement."

mkdir -p "${RAW_DIR}"

log()
{
  printf '[PAPER-11][%s] %s\n' "$(date +%H:%M:%S)" "$*"
}

die()
{
  log "ERROR: $*"
  exit 1
}

run_optional_setup()
{
  if [ "${SETUP}" != "1" ]; then
    return 0
  fi

  log "Running RFsim setup through redcap_mmtc_smoke_validation.sh"
  (
    cd "${REPO_ROOT}"
    MMTC_TOTAL_UES=${P11_SETUP_TOTAL_UES:-29} \
    MMTC_SAMPLE_UES="${UE_INDEX}" \
    MMTC_IPERF_ENABLE=0 \
    MMTC_FORWARD_PING_MODE=parallel \
    MMTC_RUN_REVERSE_PING=0 \
    MMTC_PUCCH_COMMON_FALLBACK_BWP0=1 \
    MMTC_REDCAP_ENABLE=1 \
    MMTC_REDCAP_NUM_RX=1 \
    MMTC_REDCAP_HALF_DUPLEX=1 \
    bash redcap_interface/redcap_mmtc_smoke_validation.sh
  )
}

docker_exec()
{
  docker exec "$@"
}

require_container()
{
  local container="$1"
  docker inspect -f '{{.State.Running}}' "${container}" >/dev/null 2>&1 || die "missing container ${container}"
  [ "$(docker inspect -f '{{.State.Running}}' "${container}")" = "true" ] || die "container ${container} is not running"
}

container_ipv4()
{
  local container="$1"
  local iface="$2"
  docker_exec "${container}" sh -c "ip -4 -o addr show dev ${iface} | sed -E 's/.*inet ([0-9.]+)\\/.*/\\1/' | head -n 1"
}

derive_tun_peer()
{
  local ue_ip="$1"
  awk -F. '{ printf "%s.%s.%s.1\n", $1, $2, $3 }' <<< "${ue_ip}"
}

start_iperf_server()
{
  local port="$1"
  local log_path="$2"
  {
    echo "# collected_at=$(date --iso-8601=seconds)"
    echo "# container=${SERVER_CONTAINER}"
    echo "# port=${port}"
    docker_exec "${SERVER_CONTAINER}" sh -c "pids=\$(pidof iperf3 2>/dev/null || true); [ -z \"\$pids\" ] || kill \$pids; iperf3 -s -D -p ${port}"
  } > "${log_path}" 2>&1
}

iperf_protocol_args()
{
  local rate="$1"
  if [ "${PROTOCOL}" = "udp" ]; then
    printf -- '-u -b %s' "${rate}"
  else
    printf -- '-b %s' "${rate}"
  fi
}

parse_iperf_receiver()
{
  local log_path="$1"
  awk '
    function to_mbps(value, unit) {
      if (unit ~ /^Kbits/) return value / 1000.0
      if (unit ~ /^Mbits/) return value
      if (unit ~ /^Gbits/) return value * 1000.0
      return ""
    }
    / receiver/ {
      for (i = 1; i <= NF; i++) {
        if ($i ~ /bits\/sec$/ && i > 1) {
          mbps = to_mbps($(i - 1), $i)
        }
        if ($i == "ms" && i > 1) {
          jitter = $(i - 1)
        }
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
      if (mbps == "") mbps = "NA"
      if (jitter == "") jitter = "NA"
      if (lost == "") lost = "NA"
      if (total == "") total = "NA"
      if (pct == "") pct = "NA"
      printf "%s,%s,%s,%s,%s\n", mbps, jitter, lost, total, pct
    }' "${log_path}"
}

parse_ping()
{
  local log_path="$1"
  awk '
    /packet loss/ {
      for (i = 1; i <= NF; i++) {
        if ($i ~ /%$/) {
          loss = $i
          gsub(/%/, "", loss)
          break
        }
      }
    }
    /rtt min\/avg\/max/ || /round-trip min\/avg\/max/ {
      split($0, parts, "=")
      split(parts[2], vals, "/")
      avg = vals[2]
      gsub(/^[ \t]+|[ \t]+$/, "", avg)
    }
    END {
      if (loss == "") loss = "NA"
      if (avg == "") avg = "NA"
      printf "%s,%s\n", loss, avg
    }' "${log_path}"
}

append_csv_header()
{
  cat > "${CSV_PATH}" <<EOF
run_id,paper_anchor,test_id,status,direction,ue,protocol,offered_rate,duration_s,server_ip,ue_ip,receiver_mbps,jitter_ms,lost_packets,total_packets,lost_percent,ping_size_bytes,ping_loss_percent,rtt_avg_ms,log_path,limitation_note
EOF
}

append_iperf_row()
{
  local test_id="$1"
  local status="$2"
  local direction="$3"
  local rate="$4"
  local log_path="$5"
  local parsed="$6"
  local receiver_mbps jitter_ms lost_packets total_packets lost_percent
  IFS=, read -r receiver_mbps jitter_ms lost_packets total_packets lost_percent <<< "${parsed}"
  printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
    "${RUN_ID}" \
    "PAPER-11 Research on RedCap UE performance indicators" \
    "${test_id}" \
    "${status}" \
    "${direction}" \
    "${UE_INDEX}" \
    "${PROTOCOL}" \
    "${rate}" \
    "${DURATION}" \
    "${SERVER_IP}" \
    "${UE_IP}" \
    "${receiver_mbps}" \
    "${jitter_ms}" \
    "${lost_packets}" \
    "${total_packets}" \
    "${lost_percent}" \
    "NA" \
    "NA" \
    "NA" \
    "${log_path}" \
    "\"${LIMITATION_NOTE}\"" >> "${CSV_PATH}"
}

append_ping_row()
{
  local test_id="$1"
  local status="$2"
  local size="$3"
  local log_path="$4"
  local parsed="$5"
  local loss avg
  IFS=, read -r loss avg <<< "${parsed}"
  printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
    "${RUN_ID}" \
    "PAPER-11 Research on RedCap UE performance indicators" \
    "${test_id}" \
    "${status}" \
    "LAT" \
    "${UE_INDEX}" \
    "icmp" \
    "NA" \
    "NA" \
    "${PING_TARGET_IP}" \
    "${UE_IP}" \
    "NA" \
    "NA" \
    "NA" \
    "NA" \
    "NA" \
    "${size}" \
    "${loss}" \
    "${avg}" \
    "${log_path}" \
    "\"${LIMITATION_NOTE}\"" >> "${CSV_PATH}"
}

run_iperf_direction()
{
  local direction="$1"
  local rate="$2"
  local port="$3"
  local test_id="$4"
  local reverse_arg=()
  local server_log="${RAW_DIR}/${RUN_ID}_${direction}_server.log"
  local iperf_log="${RAW_DIR}/${RUN_ID}_${direction}_ue${UE_INDEX}.log"
  local proto_args=()

  if [ "${direction}" = "DL" ]; then
    reverse_arg=(-R)
  fi

  read -r -a proto_args <<< "$(iperf_protocol_args "${rate}")"
  log "Starting iperf3 server on ${SERVER_CONTAINER}:${port}"
  start_iperf_server "${port}" "${server_log}"

  log "Live ${direction} iperf3: UE=${UE_CONTAINER}, server=${SERVER_IP}, rate=${rate}, duration=${DURATION}s"
  set +e
  docker_exec "${UE_CONTAINER}" iperf3 \
    -c "${SERVER_IP}" \
    -B "${UE_IP}" \
    -p "${port}" \
    -t "${DURATION}" \
    -i 1 \
    "${proto_args[@]}" \
    "${reverse_arg[@]}" | tee "${iperf_log}"
  local rc=${PIPESTATUS[0]}
  set -e

  local status="PASS"
  if [ "${rc}" -ne 0 ]; then
    status="FAIL"
  fi
  append_iperf_row "${test_id}" "${status}" "${direction}" "${rate}" "${iperf_log}" "$(parse_iperf_receiver "${iperf_log}")"
  log "${direction} iperf3 status=${status}; log=${iperf_log}"
}

run_iperf_panel()
{
  local direction="${MODE,,}"
  local panel_dir="${RAW_DIR}/panel"

  log "Starting iperf live panel: mode=${direction}, UL=${UL_RATE}, DL=${DL_RATE}, duration=${DURATION}s"
  python3 "${PANEL_SCRIPT}" \
    --direction "${direction}" \
    --ue "${UE_INDEX}" \
    --ue-container "${UE_CONTAINER}" \
    --server-container "${SERVER_CONTAINER}" \
    --server-ip "${SERVER_IP}" \
    --ue-ip "${UE_IP}" \
    --protocol "${PROTOCOL}" \
    --ul-rate "${UL_RATE}" \
    --dl-rate "${DL_RATE}" \
    --duration "${DURATION}" \
    --base-port "${BASE_PORT}" \
    --run-id "${RUN_ID}_panel" \
    --output-dir "${panel_dir}"
  log "Panel output: ${panel_dir}"
  log "Panel CSV summary: ${panel_dir}/${RUN_ID}_panel_summary.csv"
}

run_ping_probe()
{
  local size="$1"
  local test_id="$2"
  local ping_log="${RAW_DIR}/${RUN_ID}_ping_${size}B_ue${UE_INDEX}.log"

  log "Ping probe: target=${PING_TARGET_IP}, payload=${size} bytes, count=${PING_COUNT}"
  set +e
  docker_exec "${UE_CONTAINER}" ping -I oaitun_ue1 -s "${size}" -c "${PING_COUNT}" "${PING_TARGET_IP}" | tee "${ping_log}"
  local rc=${PIPESTATUS[0]}
  set -e

  local status="PASS"
  if [ "${rc}" -ne 0 ]; then
    status="FAIL"
  fi
  append_ping_row "${test_id}" "${status}" "${size}" "${ping_log}" "$(parse_ping "${ping_log}")"
  log "Ping ${size}B status=${status}; log=${ping_log}"
}

case "${MODE}" in
  ul|UL|dl|DL|both|BOTH) ;;
  *) die "P11_MODE must be ul, dl, or both" ;;
esac

case "${PROTOCOL}" in
  udp|tcp) ;;
  *) die "P11_PROTOCOL must be udp or tcp" ;;
esac

run_optional_setup
require_container "${SERVER_CONTAINER}"
require_container "${UE_CONTAINER}"

SERVER_IP=${P11_SERVER_IP:-$(container_ipv4 "${SERVER_CONTAINER}" eth0)}
UE_IP=${P11_UE_IP:-$(container_ipv4 "${UE_CONTAINER}" oaitun_ue1)}
PING_TARGET_IP=${P11_PING_TARGET_IP:-$(derive_tun_peer "${UE_IP}")}

[ -n "${SERVER_IP}" ] || die "cannot resolve ${SERVER_CONTAINER} eth0 IPv4"
[ -n "${UE_IP}" ] || die "cannot resolve ${UE_CONTAINER} oaitun_ue1 IPv4"

append_csv_header

log "Run ID: ${RUN_ID}"
log "Raw output: ${RAW_DIR}"
log "CSV summary: ${CSV_PATH}"
log "UE tunnel IP: ${UE_IP}; iperf server IP: ${SERVER_IP}; ping target: ${PING_TARGET_IP}"

run_ping_probe 32 PERF-P11-LAT-032
run_ping_probe 1500 PERF-P11-LAT-1500

if [ "${PANEL}" = "1" ]; then
  run_iperf_panel
  log "Completed PAPER-11 live iperf demo"
  log "Ping CSV summary: ${CSV_PATH}"
  exit 0
fi

case "${MODE}" in
  ul|UL)
    run_iperf_direction UL "${UL_RATE}" "${BASE_PORT}" PERF-P11-LIVE-UL
    ;;
  dl|DL)
    run_iperf_direction DL "${DL_RATE}" "$((BASE_PORT + 1))" PERF-P11-LIVE-DL
    ;;
  both|BOTH)
    run_iperf_direction UL "${UL_RATE}" "${BASE_PORT}" PERF-P11-LIVE-UL
    run_iperf_direction DL "${DL_RATE}" "$((BASE_PORT + 1))" PERF-P11-LIVE-DL
    ;;
esac

log "Completed PAPER-11 live iperf demo"
log "CSV summary: ${CSV_PATH}"
