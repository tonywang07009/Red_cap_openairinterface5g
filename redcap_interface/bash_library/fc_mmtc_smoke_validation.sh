#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
INTERFACE_DIR=$(realpath "${SCRIPT_DIR}/..")
REPO_ROOT=$(realpath "${INTERFACE_DIR}/..")
TIMESTAMP=$(date +%F_%H-%M-%S)

TOTAL_UES=${MMTC_TOTAL_UES:-64}
SAMPLE_UES_RAW=${MMTC_SAMPLE_UES:-"29 32 64"}
EXT_DN_IP=${MMTC_EXT_DN_IP:-}
LEGACY_EXT_DN_IP=${MMTC_LEGACY_EXT_DN_IP:-12.1.1.1}
PING_COUNT=${MMTC_PING_COUNT:-10}
REVERSE_PING_COUNT=${MMTC_REVERSE_PING_COUNT:-3}
SLEEP_AFTER_UP=${MMTC_SLEEP_AFTER_UP:-25}
START_XAPP=${MMTC_START_XAPP:-0}
PREPARE_ONLY=${MMTC_SMOKE_PREPARE_ONLY:-0}
RESET_CN=${MMTC_RESET_CN:-1}
GNB_WARMUP=${MMTC_GNB_WARMUP:-5}
UE_START_GAP=${MMTC_UE_START_GAP:-3}
FORWARD_PING_MODE=${MMTC_FORWARD_PING_MODE:-serial}
RUN_REVERSE_PING=${MMTC_RUN_REVERSE_PING:-1}
IMAGE_REGISTRY=${MMTC_IMAGE_REGISTRY:-}
IMAGE_TAG=${MMTC_IMAGE_TAG:-latest}
GNB_IMAGE_NAME=${MMTC_GNB_IMAGE_NAME:-oai-gnb}
NRUE_IMAGE_NAME=${MMTC_NRUE_IMAGE_NAME:-oai-nr-ue}
AUTO_RECOVER_AFTER_GNB_RESTART=${MMTC_AUTO_RECOVER_AFTER_GNB_RESTART:-1}
AUTO_RECOVER_MISSING_UES=${MMTC_AUTO_RECOVER_MISSING_UES:-1}
RECOVER_ON_PRECHECK_GNB_RESTART=${MMTC_RECOVER_ON_PRECHECK_GNB_RESTART:-0}
FAIL_ON_GNB_RESTART=${MMTC_FAIL_ON_GNB_RESTART:-1}
RECOVERY_SETTLE=${MMTC_RECOVERY_SETTLE:-15}
RECOVERY_UE_GAP=${MMTC_RECOVERY_UE_GAP:-0}
PRECHECK_RECOVERY_UE_GAP=${MMTC_PRECHECK_RECOVERY_UE_GAP:-2}
PRECHECK_RECOVERY_SETTLE=${MMTC_PRECHECK_RECOVERY_SETTLE:-20}
ADAPTIVE_BURST_ON_ZERO_GAP=${MMTC_ADAPTIVE_BURST_ON_ZERO_GAP:-1}
UE_START_BURST_SIZE=${MMTC_UE_START_BURST_SIZE:-8}
UE_START_BURST_PAUSE=${MMTC_UE_START_BURST_PAUSE:-2}
UE_START_BURST_THRESHOLD=${MMTC_UE_START_BURST_THRESHOLD:-32}
IPERF_ENABLE=${MMTC_IPERF_ENABLE:-0}
IPERF_SAMPLE_UES_RAW=${MMTC_IPERF_SAMPLE_UES:-"${SAMPLE_UES_RAW}"}
IPERF_RATE=${MMTC_IPERF_RATE:-30M}
IPERF_DURATION=${MMTC_IPERF_DURATION:-20}
IPERF_UDP=${MMTC_IPERF_UDP:-1}
IPERF_SERVER_IP=${MMTC_IPERF_SERVER_IP:-}
IPERF_TCP_MIN_MBIT=${MMTC_IPERF_TCP_MIN_MBIT:-}
IPERF_QUIESCE_NON_SELECTED=${MMTC_IPERF_QUIESCE_NON_SELECTED:-0}
IPERF_QUIESCE_ACTION=${MMTC_IPERF_QUIESCE_ACTION:-pause}
IPERF_RETRIES=${MMTC_IPERF_RETRIES:-2}
IPERF_SERVER_SETTLE=${MMTC_IPERF_SERVER_SETTLE:-1}
USE_EXISTING_CN_DB=${MMTC_USE_EXISTING_CN_DB:-1}
MMTC_PUCCH_COMMON_FALLBACK_BWP0=${MMTC_PUCCH_COMMON_FALLBACK_BWP0:-1}
export MMTC_PUCCH_COMMON_FALLBACK_BWP0

OVERLAY_GENERATOR="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh"
CN_DB_GENERATOR="${REPO_ROOT}/redcap_interface/generate_mmtc_cn_db_overlay.sh"
BASE_COMPOSE="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml"
OVERLAY_COMPOSE="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml"
CN_COMPOSE=${MMTC_CN_COMPOSE:-/home/tonywang/OAI/oai-cn5g/docker-compose.yaml}
LOG_DIR="${REPO_ROOT}/test_log/compiler_logs"
RUNTIME_CONFIG_DIR="${REPO_ROOT}/test_log/runtime_configs"
FAILURES=0
GNB_RESTART_COUNT=0
UE_RUNNING_COUNT=0
UE_ATTACH_COUNT=0
UE_PDU_ACCEPT_COUNT=0
UE_TUN_COUNT=0
UE_FORWARD_PING_OK_COUNT=0
UE_REVERSE_PING_OK_COUNT=0
UE_IPERF_OK_COUNT=0
UE_IPERF_RUN_COUNT=0
RECOVERY_RESTARTED_UES=0

mkdir -p "${LOG_DIR}"
mkdir -p "${RUNTIME_CONFIG_DIR}"

declare -a PING_UE_INDICES=()
declare -a PING_CONTAINER_NAMES=()
declare -a PING_TARGET_IPS=()
declare -a PING_TARGET_SOURCES=()
declare -a PING_UE_IPV4S=()
declare -a PING_LOG_FILES=()
declare -a REVERSE_PING_LOG_FILES=()
declare -a IPERF_SAMPLE_UES=()
declare -A UE_LAUNCH_EPOCH_MS=()

LATENCY_CSV="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_access_latency.csv"

epoch_ms()
{
  date +%s%3N
}

apply_radio_profile_defaults()
{
  local n_rb="${MMTC_N_RB_DL:-}"
  local gnb_config="${GNB_REDCAP_CONFIG:-}"
  local expected_rf=""
  local expected_ssb=""
  local profile=""

  if [ "${n_rb}" = "51" ] || [[ "${gnb_config}" == *"51PRB"* ]]; then
    profile="51prb"
    expected_rf="3617640000"
    expected_ssb="238"
  fi

  if [ -z "${profile}" ]; then
    return 0
  fi

  if [ -z "${MMTC_RF_FREQ+x}" ]; then
    export MMTC_RF_FREQ="${expected_rf}"
    echo "[INFO] RF profile ${profile}: default MMTC_RF_FREQ=${MMTC_RF_FREQ}"
  fi
  if [ -z "${MMTC_SSB_START+x}" ]; then
    export MMTC_SSB_START="${expected_ssb}"
    echo "[INFO] RF profile ${profile}: default MMTC_SSB_START=${MMTC_SSB_START}"
  fi

  if [ "${MMTC_RF_FREQ}" != "${expected_rf}" ] || [ "${MMTC_SSB_START}" != "${expected_ssb}" ]; then
    echo "[WARN] RF profile ${profile}: expected RF/SSB ${expected_rf}/${expected_ssb}, using ${MMTC_RF_FREQ}/${MMTC_SSB_START}"
  fi
}

compose_with_images()
{
  REGISTRY="${IMAGE_REGISTRY}" \
  TAG="${IMAGE_TAG}" \
  GNB_IMG="${GNB_IMAGE_NAME}" \
  NRUE_IMG="${NRUE_IMAGE_NAME}" \
    docker compose "$@"
}

capture_cmd()
{
  local output_file="$1"
  shift
  {
    echo "# collected_at=$(date --iso-8601=seconds)"
    echo "# command: $*"
    "$@" 2>&1
  } > "${output_file}" || true
}

capture_ue_net_state()
{
  local container_name="$1"
  local output_file="$2"

  capture_cmd "${output_file}" docker exec "${container_name}" sh -c '
    echo "## ip -br address"
    ip -br address || true
    echo
    echo "## ip route"
    ip route || true
    echo
    echo "## ip rule"
    ip rule show || true
    echo
    echo "## ip -s link show dev oaitun_ue1"
    ip -s link show dev oaitun_ue1 || true
    echo
    echo "## ip -s link show dev eth0"
    ip -s link show dev eth0 || true
    echo
    echo "## /proc/net/dev"
    cat /proc/net/dev || true
  '
}

capture_shared_user_plane_snapshot()
{
  local phase="$1"
  capture_container_snapshot "gNB-${phase}" "rfsim5g-oai-gnb_redcap" "${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_gnb_${phase}.log"
  capture_container_snapshot "UPF-${phase}" "oai-upf" "${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_upf_${phase}.log"
  capture_container_snapshot "ext-dn-${phase}" "oai-ext-dn" "${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_extdn_${phase}.log"
}

run_reverse_ping_for_ue()
{
  local ue_idx="$1"
  local ue_tun_ipv4="$2"
  local reverse_ping_log="$3"

  if [ "${RUN_REVERSE_PING}" != "1" ] || [ -z "${ue_tun_ipv4}" ]; then
    return 0
  fi

  echo "[INFO] Reverse ping from ext-dn to ${ue_tun_ipv4}"
  if ! docker exec oai-ext-dn ping -c "${REVERSE_PING_COUNT}" "${ue_tun_ipv4}" | tee "${reverse_ping_log}"; then
    echo "[WARN] Reverse ping from ext-dn to ${ue_tun_ipv4} failed"
    FAILURES=$((FAILURES + 1))
    return 1
  fi

  UE_REVERSE_PING_OK_COUNT=$((UE_REVERSE_PING_OK_COUNT + 1))
  return 0
}

run_parallel_forward_pings()
{
  local -a pids=()

  echo "[INFO] Starting parallel forward ping for ${#PING_CONTAINER_NAMES[@]} UE(s)"

  for idx in "${!PING_CONTAINER_NAMES[@]}"; do
    local container_name="${PING_CONTAINER_NAMES[$idx]}"
    local target_ip="${PING_TARGET_IPS[$idx]}"
    local target_source="${PING_TARGET_SOURCES[$idx]}"
    local ue_ipv4="${PING_UE_IPV4S[$idx]}"
    local ping_log="${PING_LOG_FILES[$idx]}"

    echo "[INFO] Parallel ping ${container_name} -> ${target_ip} (source=${target_source}, UE IPv4=${ue_ipv4:-unknown})"
    (
      docker exec "${container_name}" ping -I oaitun_ue1 -c "${PING_COUNT}" "${target_ip}"
    ) | tee "${ping_log}" &
    pids+=($!)
  done

  for idx in "${!pids[@]}"; do
    local ue_idx="${PING_UE_INDICES[$idx]}"
    local container_name="${PING_CONTAINER_NAMES[$idx]}"
    local target_ip="${PING_TARGET_IPS[$idx]}"

    if ! wait "${pids[$idx]}"; then
      echo "[WARN] ${container_name} ping failed (IMSI $(printf '001010%09d' "${ue_idx}"), target ${target_ip})"
      FAILURES=$((FAILURES + 1))
    else
      UE_FORWARD_PING_OK_COUNT=$((UE_FORWARD_PING_OK_COUNT + 1))
    fi
  done
}

ue_selected_for_iperf()
{
  local ue_idx="$1"

  if [ "${IPERF_SAMPLE_UES_RAW}" = "all" ]; then
    return 0
  fi

  for selected_idx in "${IPERF_SAMPLE_UES[@]}"; do
    if [ "${selected_idx}" = "${ue_idx}" ]; then
      return 0
    fi
  done

  return 1
}

start_iperf_server()
{
  local server_log="$1"

  set +e
  {
    echo "# collected_at=$(date --iso-8601=seconds)"
    echo "# command: docker exec oai-ext-dn sh -c 'pids=\$(pidof iperf3 2>/dev/null || true); [ -z \"\$pids\" ] || kill \$pids; iperf3 -s -D'"
    docker exec oai-ext-dn sh -c 'pids=$(pidof iperf3 2>/dev/null || true); [ -z "$pids" ] || kill $pids; iperf3 -s -D'
  } > "${server_log}" 2>&1
  local rc=$?
  set -e
  if [ "${rc}" -eq 0 ] && [ "${IPERF_SERVER_SETTLE}" -gt 0 ]; then
    sleep "${IPERF_SERVER_SETTLE}"
  fi
  return "${rc}"
}

resolve_iperf_server_ip()
{
  if [ -n "${IPERF_SERVER_IP}" ]; then
    printf '%s\n' "${IPERF_SERVER_IP}"
    return 0
  fi

  docker exec oai-ext-dn sh -c "ip -4 -o addr show dev eth0 | sed -E 's/.*inet ([0-9.]+)\\/.*/\\1/' | head -n 1"
}

iperf_udp_sender_completed()
{
  local iperf_log="$1"

  grep -Eq 'sender$| sender' "${iperf_log}" && \
    ! grep -Eqi 'unable to connect|connection refused|no route|network is unreachable|name or service' "${iperf_log}"
}

iperf_rate_to_mbit()
{
  local rate="$1"

  awk -v rate="${rate}" '
    BEGIN {
      value = rate
      unit = rate
      gsub(/[^0-9.].*/, "", value)
      gsub(/^[0-9.]+/, "", unit)
      unit = toupper(unit)
      if (value == "") {
        print "0"
        exit
      }
      if (unit ~ /^G/) {
        printf "%.6f\n", value * 1000
      } else if (unit ~ /^K/) {
        printf "%.6f\n", value / 1000
      } else {
        printf "%.6f\n", value
      }
    }'
}

iperf_tcp_receiver_mbit()
{
  local iperf_log="$1"

  awk '
    / receiver$/ {
      for (i = 1; i <= NF; i++) {
        if ($i ~ /bits\/sec$/ && i > 1) {
          value = $(i - 1)
          unit = $i
          if (unit ~ /^Kbits/) {
            mbps = value / 1000
          } else if (unit ~ /^Mbits/) {
            mbps = value
          } else if (unit ~ /^Gbits/) {
            mbps = value * 1000
          } else {
            mbps = 0
          }
        }
      }
    }
    END {
      if (mbps == "") {
        exit 1
      }
      printf "%.6f\n", mbps
    }' "${iperf_log}"
}

iperf_tcp_receiver_meets_target()
{
  local iperf_log="$1"
  local min_mbit="$2"
  local measured_mbit

  measured_mbit=$(iperf_tcp_receiver_mbit "${iperf_log}" || true)
  if [ -z "${measured_mbit}" ]; then
    return 1
  fi

  awk -v measured="${measured_mbit}" -v minimum="${min_mbit}" 'BEGIN { exit !(measured >= minimum) }'
}

quiesce_non_iperf_ues()
{
  local -n paused_ref=$1

  if [ "${IPERF_QUIESCE_NON_SELECTED}" != "1" ]; then
    return 0
  fi

  echo "[INFO] Quiescing non-selected UE containers before iperf3 using action=${IPERF_QUIESCE_ACTION}"
  for idx in "${!PING_CONTAINER_NAMES[@]}"; do
    local ue_idx="${PING_UE_INDICES[$idx]}"
    local container_name="${PING_CONTAINER_NAMES[$idx]}"

    if ue_selected_for_iperf "${ue_idx}"; then
      continue
    fi

    if [ "${IPERF_QUIESCE_ACTION}" = "stop" ]; then
      if docker stop -t 2 "${container_name}" >/dev/null 2>&1; then
        paused_ref+=("${container_name}")
      else
        echo "[WARN] Failed to stop ${container_name} before iperf3"
        FAILURES=$((FAILURES + 1))
      fi
    elif docker pause "${container_name}" >/dev/null 2>&1; then
      paused_ref+=("${container_name}")
    else
      echo "[WARN] Failed to pause ${container_name} before iperf3"
      FAILURES=$((FAILURES + 1))
    fi
  done
  echo "[INFO] Quiesced ${#paused_ref[@]} non-selected UE container(s) before iperf3"
}

resume_quiesced_ues()
{
  local -n paused_ref=$1

  if [ "${#paused_ref[@]}" -eq 0 ]; then
    return 0
  fi

  if [ "${IPERF_QUIESCE_ACTION}" = "stop" ]; then
    echo "[INFO] Leaving ${#paused_ref[@]} stopped non-selected UE container(s) down after iperf3"
    return 0
  fi

  echo "[INFO] Unpausing ${#paused_ref[@]} non-selected UE container(s) after iperf3"
  for container_name in "${paused_ref[@]}"; do
    if ! docker unpause "${container_name}" >/dev/null 2>&1; then
      echo "[WARN] Failed to unpause ${container_name} after iperf3"
      FAILURES=$((FAILURES + 1))
    fi
  done
}

run_iperf_for_selected_ues()
{
  local server_log="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_iperf_server.log"
  local selected_count=0
  local iperf_server_ip=""
  local iperf_tcp_min_mbit="${IPERF_TCP_MIN_MBIT}"
  local -a paused_ues=()

  if [ "${IPERF_ENABLE}" != "1" ]; then
    echo "[INFO] UL iperf3 validation disabled (MMTC_IPERF_ENABLE=${IPERF_ENABLE})"
    return 0
  fi

  echo "[INFO] Starting ext-dn iperf3 server for UL-only RedCap throughput validation"
  if ! start_iperf_server "${server_log}"; then
    echo "[WARN] Failed to start iperf3 server on oai-ext-dn; log=${server_log}"
    FAILURES=$((FAILURES + 1))
    return 0
  fi
  iperf_server_ip=$(resolve_iperf_server_ip || true)
  if [ -z "${iperf_server_ip}" ]; then
    echo "[WARN] Failed to resolve oai-ext-dn IPv4 address for iperf3"
    FAILURES=$((FAILURES + 1))
    return 0
  fi
  echo "[INFO] UL iperf3 server IP: ${iperf_server_ip}"

  if [ "${IPERF_UDP}" != "1" ] && [ -z "${iperf_tcp_min_mbit}" ]; then
    iperf_tcp_min_mbit=$(iperf_rate_to_mbit "${IPERF_RATE}")
  fi

  quiesce_non_iperf_ues paused_ues

  for idx in "${!PING_CONTAINER_NAMES[@]}"; do
    local ue_idx="${PING_UE_INDICES[$idx]}"
    local container_name="${PING_CONTAINER_NAMES[$idx]}"
    local target_ip="${iperf_server_ip}"
    local ue_ipv4="${PING_UE_IPV4S[$idx]}"
    local iperf_log="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_iperf3_ul.log"
    local -a iperf_args=()

    if ! ue_selected_for_iperf "${ue_idx}"; then
      continue
    fi
    if [ -z "${ue_ipv4}" ]; then
      echo "[WARN] Skip iperf3 for ${container_name}: missing UE TUN IPv4"
      FAILURES=$((FAILURES + 1))
      continue
    fi

    selected_count=$((selected_count + 1))
    UE_IPERF_RUN_COUNT=$((UE_IPERF_RUN_COUNT + 1))

    if ! start_iperf_server "${server_log}"; then
      echo "[WARN] Failed to restart iperf3 server before UE${ue_idx}; log=${server_log}"
      FAILURES=$((FAILURES + 1))
      continue
    fi

    iperf_args=(iperf3 -c "${target_ip}" -t "${IPERF_DURATION}" -B "${ue_ipv4}")
    if [ "${IPERF_UDP}" = "1" ]; then
      iperf_args+=(-u -b "${IPERF_RATE}")
    else
      iperf_args+=(-b "${IPERF_RATE}")
    fi

    echo "[INFO] UL iperf3 ${container_name} -> ${target_ip} (UE IPv4=${ue_ipv4}, udp=${IPERF_UDP}, rate=${IPERF_RATE}, duration=${IPERF_DURATION}s, tcp_min_mbit=${iperf_tcp_min_mbit:-n/a})"
    set +e
    {
      echo "# collected_at=$(date --iso-8601=seconds)"
      echo "# direction=UL"
      echo "# ue=${ue_idx}"
      echo "# container=${container_name}"
      echo "# target=${target_ip}"
      echo "# ue_ipv4=${ue_ipv4}"
      echo "# attempt=0"
      echo "# command: docker exec ${container_name} ${iperf_args[*]}"
      docker exec "${container_name}" "${iperf_args[@]}"
    } > "${iperf_log}" 2>&1
    local iperf_rc=$?
    set -e

    local retry_idx=1
    while [ "${iperf_rc}" -ne 0 ] && [ "${retry_idx}" -le "${IPERF_RETRIES}" ]; do
      echo "[WARN] ${container_name} UL iperf3 failed; retry ${retry_idx}/${IPERF_RETRIES}; log=${iperf_log}"
      if ! start_iperf_server "${server_log}"; then
        echo "[WARN] Failed to restart iperf3 server before UE${ue_idx} retry ${retry_idx}; log=${server_log}"
        break
      fi
      set +e
      {
        echo
        echo "# retry_collected_at=$(date --iso-8601=seconds)"
        echo "# attempt=${retry_idx}"
        echo "# command: docker exec ${container_name} ${iperf_args[*]}"
        docker exec "${container_name}" "${iperf_args[@]}"
      } >> "${iperf_log}" 2>&1
      iperf_rc=$?
      set -e
      retry_idx=$((retry_idx + 1))
    done

    if [ "${iperf_rc}" -ne 0 ]; then
      if [ "${IPERF_UDP}" = "1" ] && iperf_udp_sender_completed "${iperf_log}"; then
        echo "[WARN] ${container_name} UL iperf3 sender completed, but server report was unavailable; accepting sender-side UL measurement; log=${iperf_log}"
        UE_IPERF_OK_COUNT=$((UE_IPERF_OK_COUNT + 1))
      else
        echo "[WARN] ${container_name} UL iperf3 failed; log=${iperf_log}"
        FAILURES=$((FAILURES + 1))
      fi
    elif [ "${IPERF_UDP}" != "1" ]; then
      local measured_mbit
      measured_mbit=$(iperf_tcp_receiver_mbit "${iperf_log}" || true)
      if [ -z "${measured_mbit}" ]; then
        echo "[WARN] ${container_name} UL TCP iperf3 did not expose receiver throughput; log=${iperf_log}"
        FAILURES=$((FAILURES + 1))
      elif iperf_tcp_receiver_meets_target "${iperf_log}" "${iperf_tcp_min_mbit}"; then
        echo "[INFO] ${container_name} UL TCP iperf3 receiver=${measured_mbit} Mbit/s target>=${iperf_tcp_min_mbit} Mbit/s"
        UE_IPERF_OK_COUNT=$((UE_IPERF_OK_COUNT + 1))
      else
        echo "[WARN] ${container_name} UL TCP iperf3 below target: receiver=${measured_mbit} Mbit/s target>=${iperf_tcp_min_mbit} Mbit/s; log=${iperf_log}"
        FAILURES=$((FAILURES + 1))
      fi
    else
      UE_IPERF_OK_COUNT=$((UE_IPERF_OK_COUNT + 1))
    fi
  done

  if [ "${selected_count}" -eq 0 ]; then
    echo "[WARN] No selected UE matched MMTC_IPERF_SAMPLE_UES='${IPERF_SAMPLE_UES_RAW}'"
    FAILURES=$((FAILURES + 1))
  fi

  resume_quiesced_ues paused_ues

  return 0
}

capture_container_snapshot()
{
  local label="$1"
  local container_name="$2"
  local output_file="$3"

  {
    echo "# label=${label}"
    echo "# container=${container_name}"
    echo "# collected_at=$(date --iso-8601=seconds)"
    docker inspect "${container_name}" --format '{{json .State}}' 2>&1 || true
    docker exec "${container_name}" sh -c '
      echo "## ip -br address"
      ip -br address || true
      echo
      echo "## ip route"
      ip route || true
      echo
      echo "## ip rule"
      ip rule show || true
      echo
      echo "## ss -u -a -n"
      ss -u -a -n || true
      echo
      echo "## /proc/net/dev"
      cat /proc/net/dev || true
    ' 2>&1 || true
  } > "${output_file}" || true
}

capture_gnb_restart_cause()
{
  local restart_count="$1"
  local state_json
  local state_fields
  local status="unknown"
  local exit_code="unknown"
  local oom_killed="unknown"
  local state_error="none"
  local started_at="unknown"
  local finished_at="unknown"
  local marker_excerpt

  state_json=$(docker inspect rfsim5g-oai-gnb_redcap --format '{{json .State}}' 2>/dev/null || true)
  printf '%s\n' "${state_json:-inspect_failed}" > "${GNB_RESTART_STATE_JSON_LOG}"

  state_fields=$(docker inspect rfsim5g-oai-gnb_redcap --format '{{.State.Status}}|{{.State.ExitCode}}|{{.State.OOMKilled}}|{{.State.Error}}|{{.State.StartedAt}}|{{.State.FinishedAt}}' 2>/dev/null || true)
  if [ -n "${state_fields}" ]; then
    IFS='|' read -r status exit_code oom_killed state_error started_at finished_at <<EOF
${state_fields}
EOF
  fi

  docker logs --tail 300 rfsim5g-oai-gnb_redcap > "${GNB_RESTART_TAIL300_LOG}" 2>&1 || true
  marker_excerpt=$(grep -E '\\[CGDBG\\]\\[ENTRYPOINT\\]|\\[CGDBG\\]\\[SIG\\]|child exit rc=|caught fatal signal|Killed' "${GNB_RESTART_TAIL300_LOG}" | tail -n 5 | tr '\n' '; ' || true)
  marker_excerpt=$(printf '%s' "${marker_excerpt}" | sed 's/[[:space:]]\+/ /g' || true)
  if [ -z "${marker_excerpt}" ]; then
    marker_excerpt="none"
  fi
  if [ -z "${state_error}" ]; then
    state_error="none"
  fi

  echo "[CGDBG][RESTART_CAUSE] restart_count=${restart_count} status=${status} exit_code=${exit_code} oom_killed=${oom_killed} error=${state_error} started_at=${started_at} finished_at=${finished_at} state_json_log=${GNB_RESTART_STATE_JSON_LOG} gnb_tail300_log=${GNB_RESTART_TAIL300_LOG} markers=\"${marker_excerpt}\""
}

start_sample_ues()
{
  local compose_args=("$@")
  local sample_count=${#SAMPLE_UES[@]}
  local adaptive_burst=0
  local burst_size=0
  local burst_pause=0

  if [ "${UE_START_GAP}" -eq 0 ] && \
     [ "${ADAPTIVE_BURST_ON_ZERO_GAP}" = "1" ] && \
     [ "${sample_count}" -ge "${UE_START_BURST_THRESHOLD}" ]; then
    if [[ "${UE_START_BURST_SIZE}" =~ ^[1-9][0-9]*$ ]] && [[ "${UE_START_BURST_PAUSE}" =~ ^[0-9]+$ ]]; then
      adaptive_burst=1
      burst_size=${UE_START_BURST_SIZE}
      burst_pause=${UE_START_BURST_PAUSE}
      echo "[INFO] Adaptive UE start pacing enabled: sample_count=${sample_count}, burst_size=${burst_size}, burst_pause=${burst_pause}s"
    else
      echo "[WARN] Adaptive UE burst pacing disabled due to invalid config: MMTC_UE_START_BURST_SIZE='${UE_START_BURST_SIZE}' MMTC_UE_START_BURST_PAUSE='${UE_START_BURST_PAUSE}'"
    fi
  fi

  for idx in "${!SAMPLE_UES[@]}"; do
    local service_name="oai-nr-ue${SAMPLE_UES[$idx]}"
    echo "[INFO] Starting sampled UE service: ${service_name}"
    UE_LAUNCH_EPOCH_MS["${SAMPLE_UES[$idx]}"]=$(epoch_ms)
    compose_with_images "${compose_args[@]}" up -d "${service_name}"

    if [ "${UE_START_GAP}" -gt 0 ] && [ $((idx + 1)) -lt "${sample_count}" ]; then
      echo "[INFO] Waiting ${UE_START_GAP}s before launching the next sampled UE"
      sleep "${UE_START_GAP}"
    elif [ "${adaptive_burst}" = "1" ] && \
         [ "${burst_pause}" -gt 0 ] && \
         [ $((idx + 1)) -lt "${sample_count}" ] && \
         [ $(((idx + 1) % burst_size)) -eq 0 ]; then
      echo "[INFO] Adaptive burst pause ${burst_pause}s after launching $((idx + 1))/${sample_count} sampled UEs"
      sleep "${burst_pause}"
    fi
  done
}

restart_non_running_sample_ues()
{
  local compose_args=("$@")
  local restarted=0

  for ue_idx in "${SAMPLE_UES[@]}"; do
    local service_name="oai-nr-ue${ue_idx}"
    local container_name="rfsim5g-oai-nr-ue${ue_idx}_redcap"
    local ue_state
    ue_state=$(docker inspect "${container_name}" --format '{{.State.Status}}' 2>/dev/null || echo missing)
    if [ "${ue_state}" = "running" ]; then
      continue
    fi

    echo "[WARN] Recovery: ${container_name} state='${ue_state}', restarting ${service_name}"
    compose_with_images "${compose_args[@]}" up -d "${service_name}"
    restarted=$((restarted + 1))

    if [ "${RECOVERY_UE_GAP}" -gt 0 ] && [ "${restarted}" -lt "${#SAMPLE_UES[@]}" ]; then
      sleep "${RECOVERY_UE_GAP}"
    fi
  done

  RECOVERY_RESTARTED_UES=${restarted}
  echo "[INFO] Recovery restarted ${RECOVERY_RESTARTED_UES} sampled UE container(s)"
}

extract_tun_ipv4()
{
  local tun_log="$1"
  awk '/inet / {print $2; exit}' "${tun_log}" | cut -d/ -f1
}

derive_subnet_peer_ipv4()
{
  local ue_ipv4="$1"
  local o1 o2 o3 o4

  if [ -z "${ue_ipv4}" ]; then
    return 0
  fi

  IFS=. read -r o1 o2 o3 o4 <<EOF
${ue_ipv4}
EOF

  if [ -z "${o1:-}" ] || [ -z "${o2:-}" ] || [ -z "${o3:-}" ] || [ -z "${o4:-}" ]; then
    return 0
  fi

  if [ "${o4}" = "1" ]; then
    printf '%s.%s.%s.2\n' "${o1}" "${o2}" "${o3}"
    return 0
  fi

  printf '%s.%s.%s.1\n' "${o1}" "${o2}" "${o3}"
}

same_slash24_subnet()
{
  local lhs="$1"
  local rhs="$2"
  local l1 l2 l3 l4 r1 r2 r3 r4

  IFS=. read -r l1 l2 l3 l4 <<EOF
${lhs}
EOF
  IFS=. read -r r1 r2 r3 r4 <<EOF
${rhs}
EOF

  [ -n "${l1:-}" ] && [ -n "${l2:-}" ] && [ -n "${l3:-}" ] && \
  [ -n "${r1:-}" ] && [ -n "${r2:-}" ] && [ -n "${r3:-}" ] && \
  [ "${l1}.${l2}.${l3}" = "${r1}.${r2}.${r3}" ]
}

mapfile -t SAMPLE_UES < <(printf '%s\n' "${SAMPLE_UES_RAW}" | tr ', ' '\n' | sed '/^$/d')
mapfile -t IPERF_SAMPLE_UES < <(printf '%s\n' "${IPERF_SAMPLE_UES_RAW}" | tr ', ' '\n' | sed '/^$/d')

if [ "${#SAMPLE_UES[@]}" -eq 0 ]; then
  echo "No sample UEs specified via MMTC_SAMPLE_UES" >&2
  exit 1
fi

for ue_idx in "${SAMPLE_UES[@]}"; do
  if ! [[ "${ue_idx}" =~ ^[0-9]+$ ]]; then
    echo "Invalid UE index in MMTC_SAMPLE_UES: ${ue_idx}" >&2
    exit 1
  fi
done

if [ "${IPERF_SAMPLE_UES_RAW}" != "all" ]; then
  for ue_idx in "${IPERF_SAMPLE_UES[@]}"; do
    if ! [[ "${ue_idx}" =~ ^[0-9]+$ ]]; then
      echo "Invalid UE index in MMTC_IPERF_SAMPLE_UES: ${ue_idx}" >&2
      exit 1
    fi
  done
fi

if [ "${FORWARD_PING_MODE}" != "serial" ] && [ "${FORWARD_PING_MODE}" != "parallel" ]; then
  echo "Invalid MMTC_FORWARD_PING_MODE: ${FORWARD_PING_MODE}" >&2
  exit 1
fi

if [ "${IPERF_ENABLE}" != "0" ] && [ "${IPERF_ENABLE}" != "1" ]; then
  echo "Invalid MMTC_IPERF_ENABLE: ${IPERF_ENABLE}" >&2
  exit 1
fi

if [ "${IPERF_UDP}" != "0" ] && [ "${IPERF_UDP}" != "1" ]; then
  echo "Invalid MMTC_IPERF_UDP: ${IPERF_UDP}" >&2
  exit 1
fi

if [ "${USE_EXISTING_CN_DB}" != "0" ] && [ "${USE_EXISTING_CN_DB}" != "1" ]; then
  echo "Invalid MMTC_USE_EXISTING_CN_DB: ${USE_EXISTING_CN_DB}" >&2
  exit 1
fi

if [ ! -f "${CN_COMPOSE}" ]; then
  echo "CN compose file not found: ${CN_COMPOSE}" >&2
  exit 1
fi

apply_radio_profile_defaults

"${OVERLAY_GENERATOR}" "${TOTAL_UES}" "${OVERLAY_COMPOSE}"

CN_DB_SQL="${RUNTIME_CONFIG_DIR}/oai_db_mmtc_${TOTAL_UES}.sql"
CN_DB_COMPOSE_OVERLAY="${RUNTIME_CONFIG_DIR}/oai-cn5g_mmtc_${TOTAL_UES}.override.yml"
CN_COMPOSE_ARGS=(-f "${CN_COMPOSE}")
if [ "${USE_EXISTING_CN_DB}" = "0" ]; then
  "${CN_DB_GENERATOR}" "${TOTAL_UES}" "${CN_DB_SQL}" "${CN_DB_COMPOSE_OVERLAY}"
  CN_COMPOSE_ARGS+=(-f "${CN_DB_COMPOSE_OVERLAY}")
fi

SERVICE_LIST=(nearRT-RIC oai-gnb)
if [ "${START_XAPP}" = "1" ]; then
  SERVICE_LIST+=(xapp-rc-moni)
fi
for ue_idx in "${SAMPLE_UES[@]}"; do
  SERVICE_LIST+=("oai-nr-ue${ue_idx}")
done

echo "[INFO] Total UE target      : ${TOTAL_UES}"
echo "[INFO] Sample UE selection : ${SAMPLE_UES[*]}"
if [ -n "${EXT_DN_IP}" ]; then
  echo "[INFO] ext-dn IP           : ${EXT_DN_IP} (env override)"
else
  echo "[INFO] ext-dn IP           : auto-derive from UE TUN subnet; legacy fallback ${LEGACY_EXT_DN_IP}"
fi
echo "[INFO] Service list        : ${SERVICE_LIST[*]}"
echo "[INFO] CN compose          : ${CN_COMPOSE}"
if [ "${USE_EXISTING_CN_DB}" = "1" ]; then
  echo "[INFO] CN DB mode          : existing compose database, no generated mMTC subscriber overlay"
else
  echo "[INFO] CN DB overlay       : ${CN_DB_SQL}"
fi
echo "[INFO] gNB warmup          : ${GNB_WARMUP}s"
echo "[INFO] UE start gap        : ${UE_START_GAP}s"
echo "[INFO] forward ping mode   : ${FORWARD_PING_MODE}"
echo "[INFO] reverse ping        : ${RUN_REVERSE_PING}"
echo "[INFO] UL iperf3           : enable=${IPERF_ENABLE} sample=${IPERF_SAMPLE_UES_RAW} udp=${IPERF_UDP} rate=${IPERF_RATE} duration=${IPERF_DURATION}s quiesce=${IPERF_QUIESCE_NON_SELECTED}/${IPERF_QUIESCE_ACTION} retries=${IPERF_RETRIES} server_settle=${IPERF_SERVER_SETTLE}s"
echo "[INFO] UE PUCCH fallback   : bwp0_common=${MMTC_PUCCH_COMMON_FALLBACK_BWP0}"
echo "[INFO] RF profile          : n_rb=${MMTC_N_RB_DL:-default} rf=${MMTC_RF_FREQ:-default} ssb=${MMTC_SSB_START:-default}"
echo "[INFO] image selection     : REGISTRY='${IMAGE_REGISTRY}' TAG='${IMAGE_TAG}' GNB='${GNB_IMAGE_NAME}' NRUE='${NRUE_IMAGE_NAME}'"
echo "[INFO] recovery config     : restart_on_gnb_restart=${AUTO_RECOVER_AFTER_GNB_RESTART} recover_missing_ues=${AUTO_RECOVER_MISSING_UES} recover_after_precheck_restart=${RECOVER_ON_PRECHECK_GNB_RESTART} settle=${RECOVERY_SETTLE}s gap=${RECOVERY_UE_GAP}s precheck_gentle_settle=${PRECHECK_RECOVERY_SETTLE}s precheck_gentle_gap=${PRECHECK_RECOVERY_UE_GAP}s fail_on_gnb_restart=${FAIL_ON_GNB_RESTART}"
echo "[INFO] adaptive burst      : on_zero_gap=${ADAPTIVE_BURST_ON_ZERO_GAP} threshold=${UE_START_BURST_THRESHOLD} burst_size=${UE_START_BURST_SIZE} pause=${UE_START_BURST_PAUSE}s"

if [ "${PREPARE_ONLY}" = "1" ]; then
  echo "[INFO] Prepare-only mode active; overlay generated at ${OVERLAY_COMPOSE}"
  exit 0
fi

if [ "${RESET_CN}" = "1" ]; then
  compose_with_images -f "${BASE_COMPOSE}" -f "${OVERLAY_COMPOSE}" down --remove-orphans >/dev/null 2>&1 || true
  compose_with_images "${CN_COMPOSE_ARGS[@]}" rm -sfv >/dev/null 2>&1 || true
fi

compose_with_images "${CN_COMPOSE_ARGS[@]}" up -d
compose_with_images -f "${BASE_COMPOSE}" -f "${OVERLAY_COMPOSE}" up -d nearRT-RIC oai-gnb

if [ "${START_XAPP}" = "1" ]; then
  compose_with_images -f "${BASE_COMPOSE}" -f "${OVERLAY_COMPOSE}" up -d xapp-rc-moni
fi

if [ "${GNB_WARMUP}" -gt 0 ]; then
  echo "[INFO] Waiting ${GNB_WARMUP}s for gNB / nearRT-RIC warmup before UE attach"
  sleep "${GNB_WARMUP}"
fi

start_sample_ues -f "${BASE_COMPOSE}" -f "${OVERLAY_COMPOSE}"

echo "[INFO] Waiting ${SLEEP_AFTER_UP}s for sampled UEs to settle"
sleep "${SLEEP_AFTER_UP}"

PRECHECK_GNB_RESTART_COUNT=$(docker inspect rfsim5g-oai-gnb_redcap --format '{{.RestartCount}}' 2>/dev/null || echo 0)
if [ "${PRECHECK_GNB_RESTART_COUNT}" != "0" ]; then
  echo "[WARN] gNB restart detected before validation phase (restart_count=${PRECHECK_GNB_RESTART_COUNT})"
fi

SKIP_PRECHECK_RECOVERY=0
if [ "${PRECHECK_GNB_RESTART_COUNT}" != "0" ] && [ "${AUTO_RECOVER_AFTER_GNB_RESTART}" = "1" ]; then
  case "${RECOVER_ON_PRECHECK_GNB_RESTART}" in
    1)
      echo "[INFO] Precheck gNB restart recovery mode: immediate"
      ;;
    2)
      RECOVERY_UE_GAP="${PRECHECK_RECOVERY_UE_GAP}"
      RECOVERY_SETTLE="${PRECHECK_RECOVERY_SETTLE}"
      echo "[INFO] Precheck gNB restart recovery mode: gentle (gap=${RECOVERY_UE_GAP}s settle=${RECOVERY_SETTLE}s)"
      ;;
    *)
      SKIP_PRECHECK_RECOVERY=1
      echo "[INFO] Skip UE auto-recovery because gNB already restarted (set MMTC_RECOVER_ON_PRECHECK_GNB_RESTART=1 for immediate or 2 for gentle recovery)"
      ;;
  esac
fi

if [ "${SKIP_PRECHECK_RECOVERY}" != "1" ]; then
  if [ "${AUTO_RECOVER_MISSING_UES}" = "1" ] || \
     { [ "${AUTO_RECOVER_AFTER_GNB_RESTART}" = "1" ] && [ "${PRECHECK_GNB_RESTART_COUNT}" != "0" ]; }; then
    restart_non_running_sample_ues -f "${BASE_COMPOSE}" -f "${OVERLAY_COMPOSE}"
    if [ "${RECOVERY_RESTARTED_UES}" -gt 0 ] && [ "${RECOVERY_SETTLE}" -gt 0 ]; then
      echo "[INFO] Waiting ${RECOVERY_SETTLE}s for UE recovery to settle"
      sleep "${RECOVERY_SETTLE}"
    fi
  fi
fi

MYSQL_LOG="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_mysql_subscribers.log"
MYSQL_CONTAINER_LOG="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_mysql.log"
AMF_LOG="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_amf.log"
UDM_LOG="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_udm.log"
AUSF_LOG="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ausf.log"
SMF_LOG="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_smf.log"
UPF_LOG="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_upf.log"
GNB_LOG="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_gnb.log"
GNB_STATE_LOG="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_gnb_state.log"
GNB_RESTART_STATE_JSON_LOG="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_gnb_restart_state_json.log"
GNB_RESTART_TAIL300_LOG="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_gnb_restart_tail300.log"

docker logs mysql > "${MYSQL_CONTAINER_LOG}" 2>&1 || true
docker logs oai-amf > "${AMF_LOG}" 2>&1 || true
docker logs oai-udm > "${UDM_LOG}" 2>&1 || true
docker logs oai-ausf > "${AUSF_LOG}" 2>&1 || true
docker logs oai-smf > "${SMF_LOG}" 2>&1 || true
docker logs oai-upf > "${UPF_LOG}" 2>&1 || true
docker logs rfsim5g-oai-gnb_redcap > "${GNB_LOG}" 2>&1 || true
{
  echo "# collected_at=$(date --iso-8601=seconds)"
  echo "## restart_count"
  docker inspect rfsim5g-oai-gnb_redcap --format '{{.RestartCount}}' 2>&1 || true
  echo
  echo "## state_json"
  docker inspect rfsim5g-oai-gnb_redcap --format '{{json .State}}' 2>&1 || true
} > "${GNB_STATE_LOG}" || true

GNB_RESTART_COUNT=$(docker inspect rfsim5g-oai-gnb_redcap --format '{{.RestartCount}}' 2>/dev/null || echo 0)
echo "[INFO] gNB restart count : ${GNB_RESTART_COUNT} (state log: ${GNB_STATE_LOG})"
if [ "${GNB_RESTART_COUNT}" != "0" ]; then
  capture_gnb_restart_cause "${GNB_RESTART_COUNT}"
  echo "[WARN] gNB restarted ${GNB_RESTART_COUNT} time(s) during this smoke run"
  if [ "${FAIL_ON_GNB_RESTART}" = "1" ]; then
    FAILURES=$((FAILURES + 1))
  else
    echo "[INFO] MMTC_FAIL_ON_GNB_RESTART=0, restart is reported but not counted as a failure"
  fi
fi

MYSQL_STATUS=$(docker inspect mysql --format '{{.State.Status}}' 2>/dev/null || echo missing)
echo "[INFO] mysql container status : ${MYSQL_STATUS}"
if [ "${MYSQL_STATUS}" != "running" ]; then
  echo "[WARN] mysql container is not running; check ${MYSQL_CONTAINER_LOG}"
  FAILURES=$((FAILURES + 1))
fi

{
  echo "-- mysql_status ${MYSQL_STATUS}"
  for ue_idx in "${SAMPLE_UES[@]}"; do
    imsi=$(printf '001010%09d' "${ue_idx}")
    echo "-- ${imsi}"
    if [ "${MYSQL_STATUS}" = "running" ]; then
      docker exec mysql mysql -uroot -plinux -D oai_db -e "
SELECT ueid FROM AuthenticationSubscription WHERE ueid = '${imsi}';
SELECT ueid FROM SessionManagementSubscriptionData WHERE ueid = '${imsi}';
" 2>&1 || true
    else
      echo "mysql container not running"
    fi
    echo
  done
} > "${MYSQL_LOG}"

echo "ue,imsi,launch_epoch_ms,tun_observed_epoch_ms,launch_to_tun_ms,status" > "${LATENCY_CSV}"

for ue_idx in "${SAMPLE_UES[@]}"; do
  imsi=$(printf '001010%09d' "${ue_idx}")
  container_name="rfsim5g-oai-nr-ue${ue_idx}_redcap"
  tun_log="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_tun.log"
  ping_log="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_ping.log"
  reverse_ping_log="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_extdn_reverse_ping.log"
  ue_log="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_docker.log"
  ue_markers="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_markers.log"
  ue_state="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_state.log"
  ue_route="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_route.log"
  ue_rule="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_rule.log"
  ue_route_get="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_route_get.log"
  ue_net_pre="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_net_pre.log"
  ue_net_post="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_net_post.log"
  ue_target="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_target.log"
  gnb_pre="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_gnb_pre.log"
  gnb_post="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_gnb_post.log"
  upf_pre="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_upf_pre.log"
  upf_post="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_upf_post.log"
  extdn_pre="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_extdn_pre.log"
  extdn_post="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_extdn_post.log"
  ue_tun_ipv4=""
  derived_ext_dn_ip=""
  effective_ext_dn_ip=""
  target_source=""

  docker inspect "${container_name}" --format '{{json .State}}' > "${ue_state}" 2>&1 || true
  docker logs "${container_name}" > "${ue_log}" 2>&1 || true
  grep -E "Received Registration Accept|Received PDU Session Establishment Accept|Interface oaitun_ue1 successfully configured|PDU Session Establishment" "${ue_log}" > "${ue_markers}" 2>&1 || true
  docker exec "${container_name}" ip route > "${ue_route}" 2>&1 || true
  docker exec "${container_name}" ip rule show > "${ue_rule}" 2>&1 || true

  if grep -q '"Status":"running"' "${ue_state}"; then
    UE_RUNNING_COUNT=$((UE_RUNNING_COUNT + 1))
  fi
  if grep -q "Received Registration Accept" "${ue_markers}"; then
    UE_ATTACH_COUNT=$((UE_ATTACH_COUNT + 1))
  fi
  if grep -q "Received PDU Session Establishment Accept" "${ue_markers}"; then
    UE_PDU_ACCEPT_COUNT=$((UE_PDU_ACCEPT_COUNT + 1))
  fi

  echo "[INFO] Checking ${container_name} TUN interface"
  if ! docker exec "${container_name}" ip a show dev oaitun_ue1 | tee "${tun_log}"; then
    launch_ms="${UE_LAUNCH_EPOCH_MS[${ue_idx}]:-}"
    printf '%s,%s,%s,,,%s\n' "${ue_idx}" "${imsi}" "${launch_ms}" "no_tun" >> "${LATENCY_CSV}"
    echo "[WARN] ${container_name} has no oaitun_ue1 (IMSI ${imsi})"
    echo "[WARN] UE log markers: ${ue_markers}"
    echo "[WARN] UE state log: ${ue_state}"
    FAILURES=$((FAILURES + 1))
    continue
  fi
  UE_TUN_COUNT=$((UE_TUN_COUNT + 1))
  tun_observed_ms=$(epoch_ms)
  launch_ms="${UE_LAUNCH_EPOCH_MS[${ue_idx}]:-}"
  launch_to_tun_ms=""
  if [[ "${launch_ms}" =~ ^[0-9]+$ ]]; then
    launch_to_tun_ms=$((tun_observed_ms - launch_ms))
  fi
  printf '%s,%s,%s,%s,%s,%s\n' "${ue_idx}" "${imsi}" "${launch_ms}" "${tun_observed_ms}" "${launch_to_tun_ms}" "tun" >> "${LATENCY_CSV}"

  ue_tun_ipv4=$(extract_tun_ipv4 "${tun_log}")
  derived_ext_dn_ip=$(derive_subnet_peer_ipv4 "${ue_tun_ipv4}")
  if [ -n "${EXT_DN_IP}" ]; then
    effective_ext_dn_ip="${EXT_DN_IP}"
    target_source="env"
  elif [ -n "${derived_ext_dn_ip}" ]; then
    effective_ext_dn_ip="${derived_ext_dn_ip}"
    target_source="tun-derived"
  else
    effective_ext_dn_ip="${LEGACY_EXT_DN_IP}"
    target_source="legacy-default"
  fi

  {
    echo "ue_tun_ipv4=${ue_tun_ipv4:-unknown}"
    echo "derived_ext_dn_ip=${derived_ext_dn_ip:-unknown}"
    echo "effective_ext_dn_ip=${effective_ext_dn_ip}"
    echo "target_source=${target_source}"
  } > "${ue_target}"

  if [ -n "${ue_tun_ipv4}" ] && ! same_slash24_subnet "${ue_tun_ipv4}" "${effective_ext_dn_ip}"; then
    echo "[WARN] ${container_name} TUN IP ${ue_tun_ipv4} is not in the same /24 subnet as ping target ${effective_ext_dn_ip}" | tee -a "${ue_target}"
  fi

  docker exec "${container_name}" ip route get "${effective_ext_dn_ip}" > "${ue_route_get}" 2>&1 || true
  PING_UE_INDICES+=("${ue_idx}")
  PING_CONTAINER_NAMES+=("${container_name}")
  PING_TARGET_IPS+=("${effective_ext_dn_ip}")
  PING_TARGET_SOURCES+=("${target_source}")
  PING_UE_IPV4S+=("${ue_tun_ipv4}")
  PING_LOG_FILES+=("${ping_log}")
  REVERSE_PING_LOG_FILES+=("${reverse_ping_log}")

  if [ "${FORWARD_PING_MODE}" = "parallel" ]; then
    continue
  fi

  capture_ue_net_state "${container_name}" "${ue_net_pre}"
  capture_container_snapshot "gNB-pre-ping" "rfsim5g-oai-gnb_redcap" "${gnb_pre}"
  capture_container_snapshot "UPF-pre-ping" "oai-upf" "${upf_pre}"
  capture_container_snapshot "ext-dn-pre-ping" "oai-ext-dn" "${extdn_pre}"

  echo "[INFO] Pinging ${effective_ext_dn_ip} from ${container_name} (source=${target_source}, UE IPv4=${ue_tun_ipv4:-unknown})"
  if ! docker exec "${container_name}" ping -I oaitun_ue1 -c "${PING_COUNT}" "${effective_ext_dn_ip}" | tee "${ping_log}"; then
    echo "[WARN] ${container_name} ping failed (IMSI ${imsi}, target ${effective_ext_dn_ip})"
    FAILURES=$((FAILURES + 1))
  else
    UE_FORWARD_PING_OK_COUNT=$((UE_FORWARD_PING_OK_COUNT + 1))
  fi

  run_reverse_ping_for_ue "${ue_idx}" "${ue_tun_ipv4}" "${reverse_ping_log}" || true

  capture_ue_net_state "${container_name}" "${ue_net_post}"
  capture_container_snapshot "gNB-post-ping" "rfsim5g-oai-gnb_redcap" "${gnb_post}"
  capture_container_snapshot "UPF-post-ping" "oai-upf" "${upf_post}"
  capture_container_snapshot "ext-dn-post-ping" "oai-ext-dn" "${extdn_post}"
done

if [ "${FORWARD_PING_MODE}" = "parallel" ] && [ "${#PING_CONTAINER_NAMES[@]}" -gt 0 ]; then
  capture_shared_user_plane_snapshot "pre_parallel_ping"
  run_parallel_forward_pings

  if [ "${RUN_REVERSE_PING}" = "1" ]; then
    for idx in "${!PING_UE_INDICES[@]}"; do
      run_reverse_ping_for_ue "${PING_UE_INDICES[$idx]}" "${PING_UE_IPV4S[$idx]}" "${REVERSE_PING_LOG_FILES[$idx]}" || true
    done
  fi

  capture_shared_user_plane_snapshot "post_parallel_ping"
fi

run_iperf_for_selected_ues

echo "[SUMMARY] sample=${#SAMPLE_UES[@]} running=${UE_RUNNING_COUNT} attach=${UE_ATTACH_COUNT} pdu=${UE_PDU_ACCEPT_COUNT} tun=${UE_TUN_COUNT} forward_ping_ok=${UE_FORWARD_PING_OK_COUNT} reverse_ping_ok=${UE_REVERSE_PING_OK_COUNT} iperf_ul_ok=${UE_IPERF_OK_COUNT} iperf_ul_run=${UE_IPERF_RUN_COUNT} gnb_restart=${GNB_RESTART_COUNT} failures=${FAILURES} mode=${FORWARD_PING_MODE}"
echo "[INFO] Access latency CSV: ${LATENCY_CSV}"
echo "[INFO] Smoke validation completed"
echo "[INFO] Logs stored under ${LOG_DIR}"

if [ "${FAILURES}" -ne 0 ]; then
  echo "[WARN] Smoke validation reported ${FAILURES} failure(s)"
  echo "[WARN] Diagnostic logs:"
  echo "       ${MYSQL_LOG}"
  echo "       ${MYSQL_CONTAINER_LOG}"
  echo "       ${AMF_LOG}"
  echo "       ${UDM_LOG}"
  echo "       ${AUSF_LOG}"
  echo "       ${SMF_LOG}"
  echo "       ${UPF_LOG}"
  echo "       ${GNB_LOG}"
  echo "       ${GNB_STATE_LOG}"
  exit 1
fi
