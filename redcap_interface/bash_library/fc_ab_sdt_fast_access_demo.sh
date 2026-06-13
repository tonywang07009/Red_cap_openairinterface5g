#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
INTERFACE_DIR=$(realpath "${SCRIPT_DIR}/..")
REPO_ROOT=$(realpath "${INTERFACE_DIR}/..")
TIMESTAMP=$(date +%F_%H-%M-%S)

RUN_ID=${AB_SDT_RUN_ID:-"ab_sdt_fast_access_${TIMESTAMP}"}
OUT_DIR=${AB_SDT_OUTPUT_DIR:-"${REPO_ROOT}/test_log/ab_sdt_fast_access"}
COMPILER_LOG_DIR="${REPO_ROOT}/test_log/compiler_logs"
SMOKE_SCRIPT="${SCRIPT_DIR}/fc_mmtc_smoke_validation.sh"
POLICY_HOST_FILE=${AB_SDT_POLICY_HOST_FILE:-"./control/redcap_policy_case_a.yaml"}

RUN_EXPERIMENTS=${AB_SDT_RUN_EXPERIMENTS:-1}
if [ "${AB_SDT_USE_EXISTING_LOGS:-0}" = "1" ]; then
  RUN_EXPERIMENTS=0
fi
RUN_A=${AB_SDT_RUN_A:-1}
RUN_B=${AB_SDT_RUN_B:-1}

TOTAL_UES=${AB_SDT_TOTAL_UES:-${MMTC_TOTAL_UES:-29}}
SAMPLE_UE=${AB_SDT_SAMPLE_UE:-1}
SAMPLE_UES_RAW=${AB_SDT_SAMPLE_UES:-${MMTC_SAMPLE_UES:-"${SAMPLE_UE}"}}
SLEEP_AFTER_UP=${AB_SDT_SLEEP_AFTER_UP:-${MMTC_SLEEP_AFTER_UP:-25}}
GNB_WARMUP=${AB_SDT_GNB_WARMUP:-${MMTC_GNB_WARMUP:-5}}
UE_START_GAP=${AB_SDT_UE_START_GAP:-${MMTC_UE_START_GAP:-0}}
PING_COUNT=${AB_SDT_PING_COUNT:-${MMTC_PING_COUNT:-10}}
FORWARD_PING_MODE=${AB_SDT_FORWARD_PING_MODE:-${MMTC_FORWARD_PING_MODE:-parallel}}
RUN_REVERSE_PING=${AB_SDT_RUN_REVERSE_PING:-0}
IPERF_ENABLE=${AB_SDT_IPERF_ENABLE:-0}
RESET_CN=${AB_SDT_RESET_CN:-1}
FAIL_ON_GNB_RESTART=${AB_SDT_FAIL_ON_GNB_RESTART:-1}
PUCCH_COMMON_FALLBACK_BWP0=${AB_SDT_PUCCH_COMMON_FALLBACK_BWP0:-1}

SUMMARY_MD="${OUT_DIR}/${RUN_ID}_summary.md"
METRICS_CSV="${OUT_DIR}/${RUN_ID}_metrics.csv"

A_GNB_LOG=${AB_SDT_A_GNB_LOG:-}
A_UE_LOG=${AB_SDT_A_UE_LOG:-}
A_PING_LOG=${AB_SDT_A_PING_LOG:-}
A_CONSOLE_LOG=${AB_SDT_A_CONSOLE_LOG:-}
B_GNB_LOG=${AB_SDT_B_GNB_LOG:-}
B_UE_LOG=${AB_SDT_B_UE_LOG:-}
B_PING_LOG=${AB_SDT_B_PING_LOG:-}
B_CONSOLE_LOG=${AB_SDT_B_CONSOLE_LOG:-}

A_SMOKE_RC="NA"
B_SMOKE_RC="NA"
A_STATUS="SKIP"
B_STATUS="SKIP"
A_STATUS_REASON="not_run"
B_STATUS_REASON="not_run"
A_DATA_PATH_MS="NA"
B_DATA_PATH_MS="NA"
B_INACTIVE_WAIT_MS="NA"
A_PACKET_BYTES="NA"
B_PACKET_BYTES="NA"
A_TBS="NA"
B_TBS="NA"
A_GNB_RX_BYTES="NA"
B_GNB_RX_BYTES="NA"
A_RB_SIZE="NA"
B_RB_SIZE="NA"
A_MCS="NA"
B_MCS="NA"
A_PING_AVG_MS="NA"
B_PING_AVG_MS="NA"
A_PING_LOSS="NA"
B_PING_LOSS="NA"

FAILURES=0

usage()
{
  cat <<EOF
Usage: $(basename "$0")

Runs or analyzes an A/B small-data fast-access demo:
  Case A: connected UE, Gate1/2/3 off
  Case B: RRC_INACTIVE + Gate3 configured-grant SDT, Gate2 off

Primary command:
  bash redcap_interface/mmtc.display.bash sdt-ab

Useful environment variables:
  AB_SDT_RUN_EXPERIMENTS=0        Analyze supplied logs instead of running Docker
  AB_SDT_USE_EXISTING_LOGS=1      Alias for AB_SDT_RUN_EXPERIMENTS=0
  AB_SDT_RUN_A=0|1               Enable Case A
  AB_SDT_RUN_B=0|1               Enable Case B
  AB_SDT_A_GNB_LOG=<path>        Case A gNB log for analysis mode
  AB_SDT_A_UE_LOG=<path>         Case A UE log for analysis mode
  AB_SDT_A_PING_LOG=<path>       Case A ping log for analysis mode
  AB_SDT_B_GNB_LOG=<path>        Case B gNB log for analysis mode
  AB_SDT_B_UE_LOG=<path>         Case B UE log for analysis mode
  AB_SDT_B_PING_LOG=<path>       Case B ping log for analysis mode
  AB_SDT_TOTAL_UES=29
  AB_SDT_SAMPLE_UE=1
  AB_SDT_PING_COUNT=10
EOF
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

mkdir -p "${OUT_DIR}"
mkdir -p "${COMPILER_LOG_DIR}"

is_number()
{
  [[ "${1:-}" =~ ^[0-9]+([.][0-9]+)?$ ]]
}

duration_ms()
{
  local start_time="$1"
  local end_time="$2"

  if is_number "${start_time}" && is_number "${end_time}"; then
    awk -v start="${start_time}" -v end="${end_time}" 'BEGIN { printf "%.3f", (end - start) * 1000.0 }'
  else
    printf 'NA'
  fi
}

csv_escape()
{
  local value="${1:-}"
  value=${value//\"/\"\"}
  printf '"%s"' "${value}"
}

append_csv_row()
{
  local first=1
  local value

  for value in "$@"; do
    if [ "${first}" -eq 0 ]; then
      printf ',' >> "${METRICS_CSV}"
    fi
    csv_escape "${value}" >> "${METRICS_CSV}"
    first=0
  done
  printf '\n' >> "${METRICS_CSV}"
}

first_sample_ue()
{
  printf '%s\n' "$1" | tr ', ' '\n' | awk 'NF {print; exit}'
}

FIRST_SAMPLE_UE=$(first_sample_ue "${SAMPLE_UES_RAW}")
if [ -z "${FIRST_SAMPLE_UE}" ]; then
  echo "No UE index found in AB_SDT_SAMPLE_UES/MMTC_SAMPLE_UES" >&2
  exit 1
fi

line_first()
{
  local log_file="$1"
  local pattern="$2"

  if [ -z "${log_file}" ] || [ ! -f "${log_file}" ]; then
    return 0
  fi

  grep -m 1 -E "${pattern}" "${log_file}" 2>/dev/null || true
}

line_first_after()
{
  local log_file="$1"
  local pattern="$2"
  local min_time="$3"

  if [ -z "${log_file}" ] || [ ! -f "${log_file}" ]; then
    return 0
  fi

  if ! is_number "${min_time}"; then
    line_first "${log_file}" "${pattern}"
    return 0
  fi

  awk -v pat="${pattern}" -v min="${min_time}" '$0 ~ pat && ($1 + 0.0) >= (min + 0.0) {print; exit}' "${log_file}" 2>/dev/null || true
}

line_time()
{
  local line="$1"
  local first

  first=$(printf '%s\n' "${line}" | awk '{print $1}')
  if is_number "${first}"; then
    printf '%s\n' "${first}"
  fi
}

word_after()
{
  local line="$1"
  local key="$2"

  printf '%s\n' "${line}" | awk -v key="${key}" '{
    for (i = 1; i <= NF; ++i) {
      if ($i == key && (i + 1) <= NF) {
        print $(i + 1)
        exit
      }
    }
  }' | sed -E 's/[^A-Za-z0-9_.:-].*$//'
}

setupcomplete_bytes()
{
  local line="$1"

  printf '%s\n' "${line}" | sed -nE 's/.*bytes([0-9]+).*/\1/p'
}

classifier_value()
{
  local line="$1"

  printf '%s\n' "${line}" | sed -nE 's/.*classifier=([^ ]+).*/\1/p'
}

ping_avg_ms()
{
  local ping_log="$1"

  if [ -z "${ping_log}" ] || [ ! -f "${ping_log}" ]; then
    return 0
  fi

  awk -F'= ' '/rtt min\/avg\/max\/mdev/ {
    split($2, values, "/")
    print values[2]
    exit
  }' "${ping_log}" 2>/dev/null || true
}

ping_loss()
{
  local ping_log="$1"

  if [ -z "${ping_log}" ] || [ ! -f "${ping_log}" ]; then
    return 0
  fi

  sed -nE 's/.* ([0-9.]+% packet loss).*/\1/p' "${ping_log}" | head -n 1
}

ping_reply_bytes()
{
  local ping_log="$1"

  if [ -z "${ping_log}" ] || [ ! -f "${ping_log}" ]; then
    return 0
  fi

  awk '/bytes from/ {print $1; exit}' "${ping_log}" 2>/dev/null || true
}

has_pattern()
{
  local log_file="$1"
  local pattern="$2"

  [ -n "${log_file}" ] && [ -f "${log_file}" ] && grep -q -E "${pattern}" "${log_file}" 2>/dev/null
}

append_reason()
{
  local current="$1"
  local item="$2"

  if [ -z "${current}" ]; then
    printf '%s' "${item}"
  else
    printf '%s;%s' "${current}" "${item}"
  fi
}

check_required()
{
  local reason="$1"
  local value="$2"
  local label="$3"

  if [ -z "${value}" ] || [ "${value}" = "NA" ]; then
    append_reason "${reason}" "missing:${label}"
  else
    printf '%s' "${reason}"
  fi
}

check_no_exit139()
{
  local reason="$1"
  shift
  local log_file

  for log_file in "$@"; do
    if has_pattern "${log_file}" 'exit 139|Segmentation fault|caught fatal signal|fatal signal'; then
      reason=$(append_reason "${reason}" "exit139_or_fatal:${log_file}")
    fi
  done

  printf '%s' "${reason}"
}

smoke_rc_reason()
{
  local reason="$1"
  local rc="$2"

  if [ "${rc}" != "NA" ] && [ "${rc}" != "0" ]; then
    append_reason "${reason}" "smoke_rc:${rc}"
  else
    printf '%s' "${reason}"
  fi
}

status_from_reason()
{
  local reason="$1"

  if [ -z "${reason}" ]; then
    printf 'PASS'
  else
    printf 'FAIL'
  fi
}

find_latest_gnb_log_after()
{
  local start_epoch="$1"

  find "${COMPILER_LOG_DIR}" -maxdepth 1 -type f -name 'mmtc_smoke_*_gnb.log' -newermt "@${start_epoch}" -printf '%T@ %p\n' 2>/dev/null \
    | sort -nr \
    | awk 'NR == 1 {sub(/^[^ ]+ /, ""); print; exit}'
}

timestamp_from_gnb_log()
{
  local gnb_log="$1"
  local base

  base=$(basename "${gnb_log}")
  printf '%s\n' "${base}" | sed -E 's/^mmtc_smoke_(.*)_gnb[.]log$/\1/'
}

ue_log_from_gnb_log()
{
  local gnb_log="$1"
  local ue_idx="$2"
  local ts

  if [ -z "${gnb_log}" ]; then
    return 0
  fi

  ts=$(timestamp_from_gnb_log "${gnb_log}")
  printf '%s/mmtc_smoke_%s_ue%s_docker.log\n' "${COMPILER_LOG_DIR}" "${ts}" "${ue_idx}"
}

ping_log_from_gnb_log()
{
  local gnb_log="$1"
  local ue_idx="$2"
  local ts

  if [ -z "${gnb_log}" ]; then
    return 0
  fi

  ts=$(timestamp_from_gnb_log "${gnb_log}")
  printf '%s/mmtc_smoke_%s_ue%s_ping.log\n' "${COMPILER_LOG_DIR}" "${ts}" "${ue_idx}"
}

run_smoke_case()
{
  local case_id="$1"
  local gate1="$2"
  local gate2="$3"
  local gate3="$4"
  local console_log="${OUT_DIR}/${RUN_ID}_${case_id}_console.log"
  local start_epoch
  local rc
  local gnb_log
  local ue_log
  local ping_log

  if [ ! -f "${SMOKE_SCRIPT}" ]; then
    echo "Smoke validation script not found: ${SMOKE_SCRIPT}" >&2
    exit 1
  fi

  start_epoch=$(date +%s)
  echo "[INFO] Running Case ${case_id}; gate1=${gate1} gate2=${gate2} gate3=${gate3} console=${console_log}"

  set +e
  env \
    REDCAP_CASE=case_a \
    REDCAP_POLICY_HOST_FILE="${POLICY_HOST_FILE}" \
    MMTC_TOTAL_UES="${TOTAL_UES}" \
    MMTC_SAMPLE_UES="${SAMPLE_UES_RAW}" \
    MMTC_SLEEP_AFTER_UP="${SLEEP_AFTER_UP}" \
    MMTC_GNB_WARMUP="${GNB_WARMUP}" \
    MMTC_UE_START_GAP="${UE_START_GAP}" \
    MMTC_PING_COUNT="${PING_COUNT}" \
    MMTC_FORWARD_PING_MODE="${FORWARD_PING_MODE}" \
    MMTC_RUN_REVERSE_PING="${RUN_REVERSE_PING}" \
    MMTC_IPERF_ENABLE="${IPERF_ENABLE}" \
    MMTC_RESET_CN="${RESET_CN}" \
    MMTC_AUTO_RECOVER_AFTER_GNB_RESTART=0 \
    MMTC_AUTO_RECOVER_MISSING_UES=0 \
    MMTC_RECOVER_ON_PRECHECK_GNB_RESTART=0 \
    MMTC_FAIL_ON_GNB_RESTART="${FAIL_ON_GNB_RESTART}" \
    MMTC_RRC_INACTIVE_GATE1_TRIGGER="${gate1}" \
    MMTC_RRC_INACTIVE_GATE2_RESUME_TRIGGER="${gate2}" \
    MMTC_RRC_INACTIVE_GATE3_CG_CONFIG="${gate3}" \
    MMTC_PUCCH_COMMON_FALLBACK_BWP0="${PUCCH_COMMON_FALLBACK_BWP0}" \
    bash "${SMOKE_SCRIPT}" 2>&1 | tee "${console_log}"
  rc=${PIPESTATUS[0]}
  set -e

  gnb_log=$(find_latest_gnb_log_after "${start_epoch}" || true)
  ue_log=$(ue_log_from_gnb_log "${gnb_log}" "${FIRST_SAMPLE_UE}")
  ping_log=$(ping_log_from_gnb_log "${gnb_log}" "${FIRST_SAMPLE_UE}")

  case "${case_id}" in
    A)
      A_SMOKE_RC="${rc}"
      A_CONSOLE_LOG="${console_log}"
      A_GNB_LOG="${gnb_log}"
      A_UE_LOG="${ue_log}"
      A_PING_LOG="${ping_log}"
      ;;
    B)
      B_SMOKE_RC="${rc}"
      B_CONSOLE_LOG="${console_log}"
      B_GNB_LOG="${gnb_log}"
      B_UE_LOG="${ue_log}"
      B_PING_LOG="${ping_log}"
      ;;
    *)
      echo "Unknown case id: ${case_id}" >&2
      exit 1
      ;;
  esac

  echo "[INFO] Case ${case_id} smoke rc=${rc} gnb_log=${gnb_log:-NA}"
}

analyse_case_a()
{
  local setup_line
  local setup_complete_line
  local reg_line
  local pdu_line
  local tun_line
  local setup_time
  local tun_time
  local reason=""

  setup_line=$(line_first "${A_UE_LOG}" 'Received NR_RRCSetup')
  setup_complete_line=$(line_first "${A_UE_LOG}" 'Generating RRCSetupComplete')
  reg_line=$(line_first "${A_UE_LOG}" 'Received Registration Accept')
  pdu_line=$(line_first "${A_UE_LOG}" 'Received PDU Session Establishment Accept')
  tun_line=$(line_first "${A_UE_LOG}" 'Interface oaitun_ue1 successfully configured')

  setup_time=$(line_time "${setup_line}")
  tun_time=$(line_time "${tun_line}")
  A_DATA_PATH_MS=$(duration_ms "${setup_time}" "${tun_time}")
  A_PACKET_BYTES=$(setupcomplete_bytes "${setup_complete_line}")
  if [ -z "${A_PACKET_BYTES}" ]; then
    A_PACKET_BYTES=$(ping_reply_bytes "${A_PING_LOG}")
  fi
  if [ -z "${A_PACKET_BYTES}" ]; then
    A_PACKET_BYTES="NA"
  fi
  A_PING_AVG_MS=$(ping_avg_ms "${A_PING_LOG}")
  if [ -z "${A_PING_AVG_MS}" ]; then
    A_PING_AVG_MS="NA"
  fi
  A_PING_LOSS=$(ping_loss "${A_PING_LOG}")
  if [ -z "${A_PING_LOSS}" ]; then
    A_PING_LOSS="NA"
  fi

  reason=$(check_required "${reason}" "${setup_line}" "UE Received NR_RRCSetup")
  reason=$(check_required "${reason}" "${setup_complete_line}" "UE Generating RRCSetupComplete")
  reason=$(check_required "${reason}" "${reg_line}" "UE Registration Accept")
  reason=$(check_required "${reason}" "${pdu_line}" "UE PDU Session Establishment Accept")
  reason=$(check_required "${reason}" "${tun_line}" "UE TUN configured")
  reason=$(check_required "${reason}" "${A_PING_AVG_MS}" "ping avg RTT")

  if has_pattern "${A_UE_LOG}" 'RRC_INACTIVE entered|configuredGrantConfig parsed|cg-SDT'; then
    reason=$(append_reason "${reason}" "unexpected_sdt_marker_in_case_a")
  fi
  if has_pattern "${A_GNB_LOG}" 'cg-SDT PUSCH rx candidate'; then
    reason=$(append_reason "${reason}" "unexpected_gnb_sdt_rx_in_case_a")
  fi
  reason=$(smoke_rc_reason "${reason}" "${A_SMOKE_RC}")
  reason=$(check_no_exit139 "${reason}" "${A_GNB_LOG}" "${A_UE_LOG}" "${A_CONSOLE_LOG}")

  A_STATUS_REASON="${reason:-ok}"
  A_STATUS=$(status_from_reason "${reason}")
  if [ "${A_STATUS}" != "PASS" ]; then
    FAILURES=$((FAILURES + 1))
  fi
}

analyse_case_b()
{
  local cfg_line
  local inactive_line
  local scheduled_line
  local tx_line
  local rx_line
  local inactive_time
  local scheduled_time
  local tx_time
  local reason=""

  cfg_line=$(line_first "${B_UE_LOG}" 'configuredGrantConfig parsed')
  inactive_line=$(line_first "${B_UE_LOG}" 'RRC_INACTIVE entered')
  inactive_time=$(line_time "${inactive_line}")
  scheduled_line=$(line_first_after "${B_UE_LOG}" 'cg-SDT autonomous CG PUSCH scheduled' "${inactive_time}")
  tx_line=$(line_first_after "${B_UE_LOG}" 'cg-SDT PUSCH tx' "${inactive_time}")
  scheduled_time=$(line_time "${scheduled_line}")
  tx_time=$(line_time "${tx_line}")
  rx_line=$(line_first_after "${B_GNB_LOG}" 'cg-SDT PUSCH rx candidate' "${inactive_time}")

  B_INACTIVE_WAIT_MS=$(duration_ms "${inactive_time}" "${tx_time}")
  B_DATA_PATH_MS=$(duration_ms "${scheduled_time}" "${tx_time}")
  B_PACKET_BYTES=$(word_after "${scheduled_line}" "bytes")
  B_TBS=$(word_after "${scheduled_line}" "tbs")
  B_RB_SIZE=$(word_after "${scheduled_line}" "rb_size")
  B_MCS=$(word_after "${scheduled_line}" "mcs")
  B_GNB_RX_BYTES=$(word_after "${rx_line}" "bytes")
  if [ -z "${B_PACKET_BYTES}" ]; then B_PACKET_BYTES="NA"; fi
  if [ -z "${B_TBS}" ]; then B_TBS="NA"; fi
  if [ -z "${B_RB_SIZE}" ]; then B_RB_SIZE="NA"; fi
  if [ -z "${B_MCS}" ]; then B_MCS="NA"; fi
  if [ -z "${B_GNB_RX_BYTES}" ]; then B_GNB_RX_BYTES="NA"; fi
  B_PING_AVG_MS=$(ping_avg_ms "${B_PING_LOG}")
  if [ -z "${B_PING_AVG_MS}" ]; then
    B_PING_AVG_MS="NA"
  fi
  B_PING_LOSS=$(ping_loss "${B_PING_LOG}")
  if [ -z "${B_PING_LOSS}" ]; then
    B_PING_LOSS="NA"
  fi

  reason=$(check_required "${reason}" "${cfg_line}" "UE configuredGrantConfig parsed")
  reason=$(check_required "${reason}" "${inactive_line}" "UE RRC_INACTIVE entered")
  reason=$(check_required "${reason}" "${scheduled_line}" "UE cg-SDT scheduled")
  reason=$(check_required "${reason}" "${tx_line}" "UE cg-SDT PUSCH tx")
  reason=$(check_required "${reason}" "${rx_line}" "gNB cg-SDT PUSCH rx candidate")
  reason=$(check_required "${reason}" "${B_PACKET_BYTES}" "SDT packet bytes")
  reason=$(check_required "${reason}" "${B_TBS}" "SDT TBS")
  reason=$(smoke_rc_reason "${reason}" "${B_SMOKE_RC}")
  reason=$(check_no_exit139 "${reason}" "${B_GNB_LOG}" "${B_UE_LOG}" "${B_CONSOLE_LOG}")

  B_STATUS_REASON="${reason:-ok}"
  B_STATUS=$(status_from_reason "${reason}")
  if [ "${B_STATUS}" != "PASS" ]; then
    FAILURES=$((FAILURES + 1))
  fi
}

append_case_row()
{
  local case_id="$1"
  local case_name="$2"
  local status="$3"
  local status_reason="$4"
  local smoke_rc="$5"
  local start_marker="$6"
  local first_data_marker="$7"
  local data_path_ms="$8"
  local inactive_wait_ms="$9"
  local packet_bytes="${10}"
  local tbs="${11}"
  local gnb_rx_bytes="${12}"
  local rb_size="${13}"
  local mcs="${14}"
  local ping_avg="${15}"
  local ping_loss_value="${16}"
  local gnb_log="${17}"
  local ue_log="${18}"
  local ping_log="${19}"
  local console_log="${20}"

  append_csv_row \
    "${case_id}" \
    "${case_name}" \
    "${status}" \
    "${status_reason}" \
    "${smoke_rc}" \
    "${start_marker}" \
    "${first_data_marker}" \
    "${data_path_ms}" \
    "${inactive_wait_ms}" \
    "${packet_bytes}" \
    "${tbs}" \
    "${gnb_rx_bytes}" \
    "${rb_size}" \
    "${mcs}" \
    "${ping_avg}" \
    "${ping_loss_value}" \
    "${gnb_log:-NA}" \
    "${ue_log:-NA}" \
    "${ping_log:-NA}" \
    "${console_log:-NA}"

  printf '| `%s` | `%s` | `%s` | `%s` | `%s` | `%s` | `%s` | `%s` | `%s` | `%s` |\n' \
    "${case_id}" "${case_name}" "${status}" "${data_path_ms}" "${inactive_wait_ms}" "${packet_bytes}" "${tbs}" "${gnb_rx_bytes}" "${ping_avg}" "${status_reason}" >> "${SUMMARY_MD}"
}

init_outputs()
{
  {
    echo "# A/B SDT Fast Access Demo"
    echo
    echo "- [Run ID]: \`${RUN_ID}\`"
    echo "- [Generated At]: \`$(date --iso-8601=seconds)\`"
    echo "- [Output Dir]: \`${OUT_DIR}\`"
    echo "- [Run Experiments]: \`${RUN_EXPERIMENTS}\`"
    echo "- [Case A]: [Connected UE], Gate1/2/3 off"
    echo "- [Case B]: [SDT UE], Gate1 on, Gate2 off, Gate3 on"
    echo "- [Total UEs]: \`${TOTAL_UES}\`"
    echo "- [Sample UEs]: \`${SAMPLE_UES_RAW}\`"
    echo "- [First Sample UE For UE/Ping Logs]: \`${FIRST_SAMPLE_UE}\`"
    echo
    echo "## Measurement Definition"
    echo "- [Case A data_path_ms]: UE \`Received NR_RRCSetup\` -> UE \`Interface oaitun_ue1 successfully configured\`."
    echo "- [Case A packet_bytes]: UE \`RRCSetupComplete\` encoded bytes when available; otherwise first ping reply bytes."
    echo "- [Case B data_path_ms]: UE \`cg-SDT autonomous CG PUSCH scheduled\` -> UE \`cg-SDT PUSCH tx\`."
    echo "- [Case B inactive_wait_ms]: UE \`RRC_INACTIVE entered\` -> UE \`cg-SDT PUSCH tx\`; this includes inactive dwell time before small data arrives."
    echo "- [Case B packet_bytes/TBS]: first UE \`cg-SDT autonomous CG PUSCH scheduled\` after inactive."
    echo "- [gNB rx bytes]: first gNB \`cg-SDT PUSCH rx candidate\` selected after the UE inactive timestamp when possible."
    echo "- [Caution]: UE and gNB timestamps are not used for hard cross-container latency unless clock alignment is proven."
    echo
    echo "## A/B Table"
    echo
    echo "| Case | Name | Status | Data path ms | Inactive wait ms | Packet bytes | TBS | gNB rx bytes | Ping avg ms | Reason |"
    echo "|---|---|---|---:|---:|---:|---:|---:|---:|---|"
  } > "${SUMMARY_MD}"

  : > "${METRICS_CSV}"
  append_csv_row case_id case_name status status_reason smoke_rc start_marker first_data_marker data_path_ms inactive_wait_ms packet_bytes tbs gnb_rx_bytes rb_size mcs ping_avg_ms ping_loss gnb_log ue_log ping_log console_log
}

write_evidence()
{
  {
    echo
    echo "## Evidence Logs"
    echo "- [Case A gNB log]: \`${A_GNB_LOG:-NA}\`"
    echo "- [Case A UE log]: \`${A_UE_LOG:-NA}\`"
    echo "- [Case A ping log]: \`${A_PING_LOG:-NA}\`"
    echo "- [Case A console log]: \`${A_CONSOLE_LOG:-NA}\`"
    echo "- [Case B gNB log]: \`${B_GNB_LOG:-NA}\`"
    echo "- [Case B UE log]: \`${B_UE_LOG:-NA}\`"
    echo "- [Case B ping log]: \`${B_PING_LOG:-NA}\`"
    echo "- [Case B console log]: \`${B_CONSOLE_LOG:-NA}\`"
    echo
    echo "## Output Files"
    echo "- [Summary]: \`${SUMMARY_MD}\`"
    echo "- [Metrics CSV]: \`${METRICS_CSV}\`"
  } >> "${SUMMARY_MD}"
}

print_console_table()
{
  echo
  printf '%-6s %-18s %-6s %-14s %-16s %-13s %-8s %-13s %-12s %s\n' \
    "Case" "Name" "Status" "DataPath(ms)" "InactiveWait(ms)" "PktBytes" "TBS" "gNBRxBytes" "PingAvg(ms)" "Reason"
  printf '%-6s %-18s %-6s %-14s %-16s %-13s %-8s %-13s %-12s %s\n' \
    "----" "------------------" "------" "------------" "----------------" "--------" "---" "----------" "-----------" "------"
  if [ "${RUN_A}" = "1" ]; then
    printf '%-6s %-18s %-6s %-14s %-16s %-13s %-8s %-13s %-12s %s\n' \
      "A" "connected" "${A_STATUS}" "${A_DATA_PATH_MS}" "NA" "${A_PACKET_BYTES}" "${A_TBS}" "${A_GNB_RX_BYTES}" "${A_PING_AVG_MS}" "${A_STATUS_REASON}"
  fi
  if [ "${RUN_B}" = "1" ]; then
    printf '%-6s %-18s %-6s %-14s %-16s %-13s %-8s %-13s %-12s %s\n' \
      "B" "sdt-inactive" "${B_STATUS}" "${B_DATA_PATH_MS}" "${B_INACTIVE_WAIT_MS}" "${B_PACKET_BYTES}" "${B_TBS}" "${B_GNB_RX_BYTES}" "${B_PING_AVG_MS}" "${B_STATUS_REASON}"
  fi
  echo
  echo "[INFO] Summary: ${SUMMARY_MD}"
  echo "[INFO] CSV    : ${METRICS_CSV}"
}

main()
{
  init_outputs

  if [ "${RUN_EXPERIMENTS}" = "1" ]; then
    if [ "${RUN_A}" = "1" ]; then
      run_smoke_case A 0 0 0
    fi
    if [ "${RUN_B}" = "1" ]; then
      run_smoke_case B 1 0 1
    fi
  else
    echo "[INFO] Analysis-only mode; reading supplied AB_SDT_*_LOG paths"
    if [ -z "${A_UE_LOG}" ] && [ -n "${A_GNB_LOG}" ]; then
      A_UE_LOG=$(ue_log_from_gnb_log "${A_GNB_LOG}" "${FIRST_SAMPLE_UE}")
    fi
    if [ -z "${A_PING_LOG}" ] && [ -n "${A_GNB_LOG}" ]; then
      A_PING_LOG=$(ping_log_from_gnb_log "${A_GNB_LOG}" "${FIRST_SAMPLE_UE}")
    fi
    if [ -z "${B_UE_LOG}" ] && [ -n "${B_GNB_LOG}" ]; then
      B_UE_LOG=$(ue_log_from_gnb_log "${B_GNB_LOG}" "${FIRST_SAMPLE_UE}")
    fi
    if [ -z "${B_PING_LOG}" ] && [ -n "${B_GNB_LOG}" ]; then
      B_PING_LOG=$(ping_log_from_gnb_log "${B_GNB_LOG}" "${FIRST_SAMPLE_UE}")
    fi
  fi

  if [ "${RUN_A}" = "1" ]; then
    analyse_case_a
    append_case_row A connected "${A_STATUS}" "${A_STATUS_REASON}" "${A_SMOKE_RC}" \
      "UE Received NR_RRCSetup" "UE TUN configured" "${A_DATA_PATH_MS}" "NA" "${A_PACKET_BYTES}" \
      "${A_TBS}" "${A_GNB_RX_BYTES}" "${A_RB_SIZE}" "${A_MCS}" "${A_PING_AVG_MS}" "${A_PING_LOSS}" \
      "${A_GNB_LOG}" "${A_UE_LOG}" "${A_PING_LOG}" "${A_CONSOLE_LOG}"
  fi

  if [ "${RUN_B}" = "1" ]; then
    analyse_case_b
    append_case_row B sdt-inactive "${B_STATUS}" "${B_STATUS_REASON}" "${B_SMOKE_RC}" \
      "UE cg-SDT scheduled" "UE cg-SDT PUSCH tx" "${B_DATA_PATH_MS}" "${B_INACTIVE_WAIT_MS}" "${B_PACKET_BYTES}" \
      "${B_TBS}" "${B_GNB_RX_BYTES}" "${B_RB_SIZE}" "${B_MCS}" "${B_PING_AVG_MS}" "${B_PING_LOSS}" \
      "${B_GNB_LOG}" "${B_UE_LOG}" "${B_PING_LOG}" "${B_CONSOLE_LOG}"
  fi

  write_evidence
  print_console_table

  if [ "${FAILURES}" -ne 0 ]; then
    echo "[WARN] A/B SDT fast-access demo reported ${FAILURES} failing case(s)" >&2
    exit 1
  fi
}

main "$@"
