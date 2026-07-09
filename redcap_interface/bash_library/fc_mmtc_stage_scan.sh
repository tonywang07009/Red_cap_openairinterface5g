#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
INTERFACE_DIR=$(realpath "${SCRIPT_DIR}/..")
REPO_ROOT=$(realpath "${INTERFACE_DIR}/..")
SMOKE_SCRIPT="${REPO_ROOT}/redcap_interface/redcap_mmtc_smoke_validation.sh"
LOG_DIR="${REPO_ROOT}/test_log/compiler_logs"
TIMESTAMP=$(date +%F_%H-%M-%S)

TOTAL_UES_TARGET=${MMTC_TOTAL_UES_TARGET:-50}
STAGE_LIST_RAW=${MMTC_STAGE_LIST:-"50"}
START_XAPP=${MMTC_START_XAPP:-0}
FORWARD_PING_MODE=${MMTC_FORWARD_PING_MODE:-parallel}
RUN_REVERSE_PING=${MMTC_RUN_REVERSE_PING:-0}
GNB_WARMUP=${MMTC_GNB_WARMUP:-10}
UE_START_GAP=${MMTC_UE_START_GAP:-10}
SLEEP_AFTER_UP=${MMTC_SLEEP_AFTER_UP:-25}
MMTC_CGCFG_NOFREE=${MMTC_CGCFG_NOFREE:-0}
MMTC_CGCFG_DEFER_FREE_SLOTS=${MMTC_CGCFG_DEFER_FREE_SLOTS:-32}
MMTC_PUCCH_COMMON_FALLBACK_BWP0=${MMTC_PUCCH_COMMON_FALLBACK_BWP0:-1}
MMTC_PDCP_TRACE=${MMTC_PDCP_TRACE:-0}
MMTC_IPERF_RATE_USER_SET=${MMTC_IPERF_RATE+x}
MMTC_IPERF_DURATION_USER_SET=${MMTC_IPERF_DURATION+x}
MMTC_IPERF_TCP_MIN_MBIT_USER_SET=${MMTC_IPERF_TCP_MIN_MBIT+x}
MMTC_IPERF_ENABLE=${MMTC_IPERF_ENABLE:-1}
MMTC_IPERF_SAMPLE_UES=${MMTC_IPERF_SAMPLE_UES:-"1,25,50"}
MMTC_IPERF_RATE=${MMTC_IPERF_RATE:-1M}
MMTC_IPERF_DURATION=${MMTC_IPERF_DURATION:-20}
MMTC_IPERF_UDP=${MMTC_IPERF_UDP:-1}
MMTC_IPERF_SERVER_IP=${MMTC_IPERF_SERVER_IP:-}
MMTC_IPERF_TCP_MIN_MBIT=${MMTC_IPERF_TCP_MIN_MBIT:-}
MMTC_IPERF_QUIESCE_NON_SELECTED=${MMTC_IPERF_QUIESCE_NON_SELECTED:-0}
MMTC_IPERF_QUIESCE_ACTION=${MMTC_IPERF_QUIESCE_ACTION:-pause}
MMTC_IPERF_RETRIES=${MMTC_IPERF_RETRIES:-2}
MMTC_IPERF_SERVER_SETTLE=${MMTC_IPERF_SERVER_SETTLE:-1}
MMTC_IPERF_PROFILE=${MMTC_IPERF_PROFILE:-}
REBUILD_IMAGES_BEFORE_SCAN=${MMTC_REBUILD_IMAGES_BEFORE_SCAN:-1}
REBUILD_SCRIPT="${REPO_ROOT}/redcap_interface/redcap_rebuild_local_oai_images.sh"

mkdir -p "${LOG_DIR}"

case "${MMTC_IPERF_PROFILE}" in
  "")
    ;;
  "eredcap20_tcp")
    MMTC_IPERF_ENABLE=1
    if [ -z "${MMTC_IPERF_RATE_USER_SET}" ]; then
      MMTC_IPERF_RATE=20M
    fi
    if [ -z "${MMTC_IPERF_DURATION_USER_SET}" ]; then
      MMTC_IPERF_DURATION=20
    fi
    MMTC_IPERF_UDP=0
    if [ -z "${MMTC_IPERF_TCP_MIN_MBIT_USER_SET}" ]; then
      MMTC_IPERF_TCP_MIN_MBIT=20
    fi
    ;;
  *)
    echo "Unsupported MMTC_IPERF_PROFILE='${MMTC_IPERF_PROFILE}'" >&2
    exit 1
    ;;
esac

if [ ! -f "${SMOKE_SCRIPT}" ]; then
  echo "Smoke script not found: ${SMOKE_SCRIPT}" >&2
  exit 1
fi

if [ "${REBUILD_IMAGES_BEFORE_SCAN}" = "1" ]; then
  if [ ! -f "${REBUILD_SCRIPT}" ]; then
    echo "Rebuild script not found: ${REBUILD_SCRIPT}" >&2
    exit 1
  fi
  echo "[INFO] Rebuilding local OAI images before stage scan"
  bash "${REBUILD_SCRIPT}"
fi

mapfile -t STAGES < <(printf '%s\n' "${STAGE_LIST_RAW}" | tr ', ' '\n' | sed '/^$/d')
if [ "${#STAGES[@]}" -eq 0 ]; then
  echo "No stages specified via MMTC_STAGE_LIST" >&2
  exit 1
fi

SUMMARY_LOG="${LOG_DIR}/mmtc_stage_scan_${TIMESTAMP}_summary.log"

{
  echo "# mMTC stage scan summary"
  echo "# collected_at=$(date --iso-8601=seconds)"
  echo "# total_ues_target=${TOTAL_UES_TARGET}"
  echo "# stages=${STAGES[*]}"
  echo "# forward_ping_mode=${FORWARD_PING_MODE} reverse_ping=${RUN_REVERSE_PING}"
  echo "# iperf_profile=${MMTC_IPERF_PROFILE:-manual} iperf_enable=${MMTC_IPERF_ENABLE} iperf_sample_ues=${MMTC_IPERF_SAMPLE_UES} iperf_rate=${MMTC_IPERF_RATE} iperf_duration=${MMTC_IPERF_DURATION} iperf_udp=${MMTC_IPERF_UDP} iperf_tcp_min_mbit=${MMTC_IPERF_TCP_MIN_MBIT:-auto} iperf_quiesce_non_selected=${MMTC_IPERF_QUIESCE_NON_SELECTED} iperf_quiesce_action=${MMTC_IPERF_QUIESCE_ACTION} iperf_retries=${MMTC_IPERF_RETRIES} iperf_server_settle=${MMTC_IPERF_SERVER_SETTLE} iperf_server_ip=${MMTC_IPERF_SERVER_IP:-auto}"
  echo "# cgcfg_nofree=${MMTC_CGCFG_NOFREE} cgcfg_defer_free_slots=${MMTC_CGCFG_DEFER_FREE_SLOTS}"
} > "${SUMMARY_LOG}"

for stage in "${STAGES[@]}"; do
  if ! [[ "${stage}" =~ ^[0-9]+$ ]]; then
    echo "[WARN] Skip invalid stage value: ${stage}" | tee -a "${SUMMARY_LOG}"
    continue
  fi

  if [ "${stage}" -gt "${TOTAL_UES_TARGET}" ]; then
    echo "[WARN] Skip stage ${stage}: exceeds total target ${TOTAL_UES_TARGET}" | tee -a "${SUMMARY_LOG}"
    continue
  fi

  sample_ues=$(seq -s, 1 "${stage}")
  run_log="${LOG_DIR}/mmtc_stage_scan_${TIMESTAMP}_ue${stage}.log"
  echo "[INFO] Stage ${stage}: MMTC_SAMPLE_UES=1..${stage}" | tee -a "${SUMMARY_LOG}"

  set +e
  env \
    MMTC_TOTAL_UES="${TOTAL_UES_TARGET}" \
    MMTC_SAMPLE_UES="${sample_ues}" \
    MMTC_START_XAPP="${START_XAPP}" \
    MMTC_FORWARD_PING_MODE="${FORWARD_PING_MODE}" \
    MMTC_RUN_REVERSE_PING="${RUN_REVERSE_PING}" \
    MMTC_GNB_WARMUP="${GNB_WARMUP}" \
    MMTC_UE_START_GAP="${UE_START_GAP}" \
    MMTC_SLEEP_AFTER_UP="${SLEEP_AFTER_UP}" \
    MMTC_CGCFG_NOFREE="${MMTC_CGCFG_NOFREE}" \
    MMTC_CGCFG_DEFER_FREE_SLOTS="${MMTC_CGCFG_DEFER_FREE_SLOTS}" \
    MMTC_PUCCH_COMMON_FALLBACK_BWP0="${MMTC_PUCCH_COMMON_FALLBACK_BWP0}" \
    MMTC_PDCP_TRACE="${MMTC_PDCP_TRACE}" \
    MMTC_IPERF_ENABLE="${MMTC_IPERF_ENABLE}" \
    MMTC_IPERF_SAMPLE_UES="${MMTC_IPERF_SAMPLE_UES}" \
    MMTC_IPERF_RATE="${MMTC_IPERF_RATE}" \
    MMTC_IPERF_DURATION="${MMTC_IPERF_DURATION}" \
    MMTC_IPERF_UDP="${MMTC_IPERF_UDP}" \
    MMTC_IPERF_TCP_MIN_MBIT="${MMTC_IPERF_TCP_MIN_MBIT}" \
    MMTC_IPERF_QUIESCE_NON_SELECTED="${MMTC_IPERF_QUIESCE_NON_SELECTED}" \
    MMTC_IPERF_QUIESCE_ACTION="${MMTC_IPERF_QUIESCE_ACTION}" \
    MMTC_IPERF_RETRIES="${MMTC_IPERF_RETRIES}" \
    MMTC_IPERF_SERVER_SETTLE="${MMTC_IPERF_SERVER_SETTLE}" \
    MMTC_IPERF_SERVER_IP="${MMTC_IPERF_SERVER_IP}" \
    bash "${SMOKE_SCRIPT}" 2>&1 | tee "${run_log}"
  rc=${PIPESTATUS[0]}
  set -e

  summary_line=$(grep '\[SUMMARY\]' "${run_log}" | tail -n 1 || true)
  if [ -z "${summary_line}" ]; then
    summary_line="[SUMMARY] missing"
  fi

  if [ "${rc}" -eq 0 ]; then
    status="PASS"
  else
    status="FAIL"
  fi

  echo "[STAGE] ue=${stage} status=${status} rc=${rc} ${summary_line}" | tee -a "${SUMMARY_LOG}"
  echo "[STAGE] log=${run_log}" | tee -a "${SUMMARY_LOG}"
done

echo "[INFO] Stage scan summary: ${SUMMARY_LOG}"
