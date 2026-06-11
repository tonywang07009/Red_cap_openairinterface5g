#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/..")
TIMESTAMP=$(date +%F_%H-%M-%S)
RUN_ID=${RRC_BEHAVIOR_RUN_ID:-"rrc_behavior_${TIMESTAMP}"}

OUT_DIR=${RRC_BEHAVIOR_OUTPUT_DIR:-"${REPO_ROOT}/test_log/rrc_behavior"}
COMPILER_LOG_DIR="${REPO_ROOT}/test_log/compiler_logs"
SMOKE_SCRIPT="${SCRIPT_DIR}/redcap_mmtc_smoke_validation.sh"
POLICY_HOST_FILE=${RRC_BEHAVIOR_POLICY_HOST_FILE:-"./control/redcap_policy_case_a.yaml"}

RUN_EXPERIMENTS=${RRC_BEHAVIOR_RUN_EXPERIMENTS:-1}
RUN_IDLE=${RRC_BEHAVIOR_RUN_IDLE:-1}
RUN_INACTIVE=${RRC_BEHAVIOR_RUN_INACTIVE:-1}

TOTAL_UES=${RRC_BEHAVIOR_TOTAL_UES:-${MMTC_TOTAL_UES:-29}}
SAMPLE_UES_RAW=${RRC_BEHAVIOR_SAMPLE_UES:-${MMTC_SAMPLE_UES:-1}}
SLEEP_AFTER_UP=${RRC_BEHAVIOR_SLEEP_AFTER_UP:-${MMTC_SLEEP_AFTER_UP:-30}}
UE_START_GAP=${RRC_BEHAVIOR_UE_START_GAP:-${MMTC_UE_START_GAP:-0}}
PING_COUNT=${RRC_BEHAVIOR_PING_COUNT:-${MMTC_PING_COUNT:-10}}
FORWARD_PING_MODE=${RRC_BEHAVIOR_FORWARD_PING_MODE:-${MMTC_FORWARD_PING_MODE:-serial}}
RUN_REVERSE_PING=${RRC_BEHAVIOR_RUN_REVERSE_PING:-0}
IPERF_ENABLE=${RRC_BEHAVIOR_IPERF_ENABLE:-0}
RESET_CN=${RRC_BEHAVIOR_RESET_CN:-1}
FAIL_ON_GNB_RESTART=${RRC_BEHAVIOR_FAIL_ON_GNB_RESTART:-1}
PUCCH_COMMON_FALLBACK_BWP0=${RRC_BEHAVIOR_PUCCH_COMMON_FALLBACK_BWP0:-1}

SUMMARY_MD="${OUT_DIR}/${RUN_ID}_summary.md"
METRICS_CSV="${OUT_DIR}/${RUN_ID}_metrics.csv"

IDLE_GNB_LOG=${RRC_BEHAVIOR_IDLE_GNB_LOG:-}
IDLE_UE_LOG=${RRC_BEHAVIOR_IDLE_UE_LOG:-}
IDLE_CONSOLE_LOG=${RRC_BEHAVIOR_IDLE_CONSOLE_LOG:-}
INACTIVE_GNB_LOG=${RRC_BEHAVIOR_INACTIVE_GNB_LOG:-}
INACTIVE_UE_LOG=${RRC_BEHAVIOR_INACTIVE_UE_LOG:-}
INACTIVE_CONSOLE_LOG=${RRC_BEHAVIOR_INACTIVE_CONSOLE_LOG:-}

IDLE_SMOKE_RC="NA"
INACTIVE_SMOKE_RC="NA"
IDLE_RA_TO_CONNECTED_MS="NA"
IDLE_RRC_MSG_TO_CONNECTED_MS="NA"
INACTIVE_RA_TO_CONNECTED_MS="NA"
INACTIVE_RRC_MSG_TO_CONNECTED_MS="NA"

mkdir -p "${OUT_DIR}"
mkdir -p "${COMPILER_LOG_DIR}"

first_sample_ue()
{
  printf '%s\n' "$1" | tr ', ' '\n' | awk 'NF {print; exit}'
}

FIRST_SAMPLE_UE=$(first_sample_ue "${SAMPLE_UES_RAW}")
if [ -z "${FIRST_SAMPLE_UE}" ]; then
  echo "No UE index found in RRC_BEHAVIOR_SAMPLE_UES/MMTC_SAMPLE_UES" >&2
  exit 1
fi

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

metric_status()
{
  local value="$1"

  if [ "${value}" = "NA" ]; then
    printf 'FAIL'
  else
    printf 'PASS'
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

extract_first_time()
{
  local log_file="$1"
  local pattern="$2"

  if [ -z "${log_file}" ] || [ ! -f "${log_file}" ]; then
    return 0
  fi

  awk -v pat="${pattern}" '$0 ~ pat {print $1; exit}' "${log_file}" 2>/dev/null || true
}

extract_first_time_after()
{
  local log_file="$1"
  local pattern="$2"
  local min_time="$3"

  if [ -z "${log_file}" ] || [ ! -f "${log_file}" ]; then
    return 0
  fi

  if ! is_number "${min_time}"; then
    extract_first_time "${log_file}" "${pattern}"
    return 0
  fi

  awk -v pat="${pattern}" -v min="${min_time}" '$0 ~ pat && ($1 + 0.0) >= (min + 0.0) {print $1; exit}' "${log_file}" 2>/dev/null || true
}

find_latest_gnb_log_after()
{
  local start_epoch="$1"

  find "${COMPILER_LOG_DIR}" -maxdepth 1 -type f -name 'mmtc_smoke_*_gnb.log' -newermt "@${start_epoch}" -printf '%T@ %p\n' 2>/dev/null \
    | sort -nr \
    | awk 'NR == 1 {sub(/^[^ ]+ /, ""); print; exit}'
}

find_latest_gnb_log()
{
  find "${COMPILER_LOG_DIR}" -maxdepth 1 -type f -name 'mmtc_smoke_*_gnb.log' -printf '%T@ %p\n' 2>/dev/null \
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

run_smoke_mode()
{
  local mode="$1"
  local gate1="$2"
  local gate2="$3"
  local console_log="${OUT_DIR}/${RUN_ID}_${mode}_console.log"
  local start_epoch
  local rc
  local gnb_log

  start_epoch=$(date +%s)
  echo "[INFO] Running ${mode} behavior smoke; console=${console_log}"

  set +e
  env \
    REDCAP_CASE=case_a \
    REDCAP_POLICY_HOST_FILE="${POLICY_HOST_FILE}" \
    MMTC_TOTAL_UES="${TOTAL_UES}" \
    MMTC_SAMPLE_UES="${SAMPLE_UES_RAW}" \
    MMTC_SLEEP_AFTER_UP="${SLEEP_AFTER_UP}" \
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
    MMTC_PUCCH_COMMON_FALLBACK_BWP0="${PUCCH_COMMON_FALLBACK_BWP0}" \
    bash "${SMOKE_SCRIPT}" 2>&1 | tee "${console_log}"
  rc=${PIPESTATUS[0]}
  set -e

  gnb_log=$(find_latest_gnb_log_after "${start_epoch}" || true)
  if [ -z "${gnb_log}" ]; then
    echo "[WARN] Could not find gNB log for ${mode} run after epoch ${start_epoch}" | tee -a "${console_log}"
  fi

  case "${mode}" in
    idle)
      IDLE_SMOKE_RC="${rc}"
      IDLE_CONSOLE_LOG="${console_log}"
      IDLE_GNB_LOG="${gnb_log}"
      IDLE_UE_LOG=$(ue_log_from_gnb_log "${gnb_log}" "${FIRST_SAMPLE_UE}")
      ;;
    inactive)
      INACTIVE_SMOKE_RC="${rc}"
      INACTIVE_CONSOLE_LOG="${console_log}"
      INACTIVE_GNB_LOG="${gnb_log}"
      INACTIVE_UE_LOG=$(ue_log_from_gnb_log "${gnb_log}" "${FIRST_SAMPLE_UE}")
      ;;
    *)
      echo "Unknown behavior mode: ${mode}" >&2
      exit 1
      ;;
  esac

  echo "[INFO] ${mode} smoke rc=${rc} gnb_log=${gnb_log:-NA}"
}

append_metric()
{
  local mode="$1"
  local metric="$2"
  local start_marker="$3"
  local start_time="$4"
  local end_marker="$5"
  local end_time="$6"
  local gnb_log="$7"
  local ue_log="$8"
  local console_log="$9"
  local smoke_rc="${10}"
  local duration
  local status

  duration=$(duration_ms "${start_time}" "${end_time}")
  status=$(metric_status "${duration}")

  append_csv_row \
    "${mode}" \
    "${metric}" \
    "${start_marker}" \
    "${start_time:-NA}" \
    "${end_marker}" \
    "${end_time:-NA}" \
    "${duration}" \
    "${status}" \
    "${smoke_rc}" \
    "${gnb_log:-NA}" \
    "${ue_log:-NA}" \
    "${console_log:-NA}"

  printf '| `%s` | `%s` | `%s` | `%s` | `%s` | `%s` | `%s` |\n' \
    "${mode}" "${metric}" "${start_marker}" "${end_marker}" "${duration}" "${status}" "${smoke_rc}" >> "${SUMMARY_MD}"
}

analyse_idle()
{
  local gnb_log="$1"
  local ue_log="$2"
  local console_log="$3"
  local smoke_rc="$4"
  local ra_start
  local rrc_setup_sent
  local setup_complete
  local ue_setup_complete
  local ue_assisted_ms

  ra_start=$(extract_first_time "${gnb_log}" 'Initiating RA procedure')
  rrc_setup_sent=$(extract_first_time "${gnb_log}" 'Send RRC Setup')
  setup_complete=$(extract_first_time "${gnb_log}" 'Received RRCSetupComplete')
  ue_setup_complete=$(extract_first_time "${ue_log}" 'Generating RRCSetupComplete')

  IDLE_RA_TO_CONNECTED_MS=$(duration_ms "${ra_start}" "${setup_complete}")
  IDLE_RRC_MSG_TO_CONNECTED_MS=$(duration_ms "${rrc_setup_sent}" "${setup_complete}")
  ue_assisted_ms=$(duration_ms "${ue_setup_complete}" "${setup_complete}")

  append_metric idle ra_to_connected_ms 'gNB Initiating RA procedure' "${ra_start}" 'gNB Received RRCSetupComplete' "${setup_complete}" "${gnb_log}" "${ue_log}" "${console_log}" "${smoke_rc}"
  append_metric idle rrc_setup_to_connected_ms 'gNB Send RRC Setup' "${rrc_setup_sent}" 'gNB Received RRCSetupComplete' "${setup_complete}" "${gnb_log}" "${ue_log}" "${console_log}" "${smoke_rc}"
  append_metric idle ue_setupcomplete_to_gnb_connected_ms 'UE Generating RRCSetupComplete' "${ue_setup_complete}" 'gNB Received RRCSetupComplete' "${setup_complete}" "${gnb_log}" "${ue_log}" "${console_log}" "${smoke_rc}"
}

analyse_inactive()
{
  local gnb_log="$1"
  local ue_log="$2"
  local console_log="$3"
  local smoke_rc="$4"
  local release_start
  local resume_ra_start
  local resume_request
  local resume_sent
  local resume_complete
  local inactive_entered
  local ue_resume_sent

  release_start=$(extract_first_time "${gnb_log}" 'Send RRC Release suspendConfig')
  resume_ra_start=$(extract_first_time_after "${gnb_log}" 'Initiating RA procedure' "${release_start}")
  resume_request=$(extract_first_time "${gnb_log}" 'RRCResumeRequest received')
  resume_sent=$(extract_first_time "${gnb_log}" 'RRCResume sent')
  resume_complete=$(extract_first_time "${gnb_log}" 'RRCResumeComplete received; RRC_CONNECTED')
  if [ -z "${resume_complete}" ]; then
    resume_complete=$(extract_first_time "${gnb_log}" 'RRCResumeComplete received')
  fi
  inactive_entered=$(extract_first_time "${ue_log}" 'RRC_INACTIVE entered')
  ue_resume_sent=$(extract_first_time "${ue_log}" 'RRCResumeComplete sent')

  INACTIVE_RA_TO_CONNECTED_MS=$(duration_ms "${resume_ra_start}" "${resume_complete}")
  INACTIVE_RRC_MSG_TO_CONNECTED_MS=$(duration_ms "${resume_request}" "${resume_complete}")

  append_metric inactive release_to_connected_ms 'gNB Send RRC Release suspendConfig' "${release_start}" 'gNB RRCResumeComplete received' "${resume_complete}" "${gnb_log}" "${ue_log}" "${console_log}" "${smoke_rc}"
  append_metric inactive ra_to_connected_ms 'gNB resume RA Initiating RA procedure' "${resume_ra_start}" 'gNB RRCResumeComplete received' "${resume_complete}" "${gnb_log}" "${ue_log}" "${console_log}" "${smoke_rc}"
  append_metric inactive rrc_resume_request_to_connected_ms 'gNB RRCResumeRequest received' "${resume_request}" 'gNB RRCResumeComplete received' "${resume_complete}" "${gnb_log}" "${ue_log}" "${console_log}" "${smoke_rc}"
  append_metric inactive rrc_resume_sent_to_connected_ms 'gNB RRCResume sent' "${resume_sent}" 'gNB RRCResumeComplete received' "${resume_complete}" "${gnb_log}" "${ue_log}" "${console_log}" "${smoke_rc}"
  append_metric inactive ue_inactive_to_ue_resumecomplete_sent_ms 'UE RRC_INACTIVE entered' "${inactive_entered}" 'UE RRCResumeComplete sent' "${ue_resume_sent}" "${gnb_log}" "${ue_log}" "${console_log}" "${smoke_rc}"
}

write_evidence_sections()
{
  {
    echo
    echo "## IDLE Evidence"
    echo "- [gNB log]: \`${IDLE_GNB_LOG:-NA}\`"
    echo "- [UE log]: \`${IDLE_UE_LOG:-NA}\`"
    echo "- [Console log]: \`${IDLE_CONSOLE_LOG:-NA}\`"
    echo "- [Note]: This is an [RRC_IDLE initial access] proxy unless the supplied log is from a true release-to-idle reconnect run."
    echo
    echo "## INACTIVE Evidence"
    echo "- [gNB log]: \`${INACTIVE_GNB_LOG:-NA}\`"
    echo "- [UE log]: \`${INACTIVE_UE_LOG:-NA}\`"
    echo "- [Console log]: \`${INACTIVE_CONSOLE_LOG:-NA}\`"
    echo "- [Note]: [RRC_INACTIVE resume] uses Gate 1/2 markers when this script runs the experiment."
  } >> "${SUMMARY_MD}"
}

delta_ms()
{
  local inactive_ms="$1"
  local idle_ms="$2"

  if is_number "${inactive_ms}" && is_number "${idle_ms}"; then
    awk -v inactive="${inactive_ms}" -v idle="${idle_ms}" 'BEGIN { printf "%.3f", inactive - idle }'
  else
    printf 'NA'
  fi
}

write_delta_section()
{
  local delta_ra
  local delta_rrc
  local faster_ra
  local faster_rrc

  delta_ra=$(delta_ms "${INACTIVE_RA_TO_CONNECTED_MS}" "${IDLE_RA_TO_CONNECTED_MS}")
  delta_rrc=$(delta_ms "${INACTIVE_RRC_MSG_TO_CONNECTED_MS}" "${IDLE_RRC_MSG_TO_CONNECTED_MS}")

  faster_ra="NA"
  if is_number "${delta_ra}"; then
    faster_ra=$(awk -v d="${delta_ra}" 'BEGIN { if (d < 0) print "inactive_faster"; else if (d > 0) print "idle_faster"; else print "tie" }')
  fi

  faster_rrc="NA"
  if is_number "${delta_rrc}"; then
    faster_rrc=$(awk -v d="${delta_rrc}" 'BEGIN { if (d < 0) print "inactive_faster"; else if (d > 0) print "idle_faster"; else print "tie" }')
  fi

  {
    echo
    echo "## Delta"
    echo
    echo "| Comparison | Formula | Delta ms | Interpretation |"
    echo "|---|---:|---:|---|"
    echo "| RA-to-connected | inactive.ra_to_connected_ms - idle.ra_to_connected_ms | \`${delta_ra}\` | \`${faster_ra}\` |"
    echo "| RRC-message-to-connected | inactive.rrc_resume_request_to_connected_ms - idle.rrc_setup_to_connected_ms | \`${delta_rrc}\` | \`${faster_rrc}\` |"
    echo
    echo "## Output Files"
    echo "- [Summary]: \`${SUMMARY_MD}\`"
    echo "- [Metrics CSV]: \`${METRICS_CSV}\`"
  } >> "${SUMMARY_MD}"
}

init_outputs()
{
  {
    echo "# RRC Behavior Comparison"
    echo
    echo "- [Run ID]: \`${RUN_ID}\`"
    echo "- [Generated At]: \`$(date --iso-8601=seconds)\`"
    echo "- [Output Dir]: \`${OUT_DIR}\`"
    echo "- [Run Experiments]: \`${RUN_EXPERIMENTS}\`"
    echo "- [Total UEs]: \`${TOTAL_UES}\`"
    echo "- [Sample UEs]: \`${SAMPLE_UES_RAW}\`"
    echo "- [First Sample UE For UE Log]: \`${FIRST_SAMPLE_UE}\`"
    echo
    echo "## Measurement Definition"
    echo "- [IDLE ra_to_connected_ms]: gNB \`Initiating RA procedure\` -> gNB \`Received RRCSetupComplete\`."
    echo "- [IDLE rrc_setup_to_connected_ms]: gNB \`Send RRC Setup\` -> gNB \`Received RRCSetupComplete\`."
    echo "- [INACTIVE ra_to_connected_ms]: gNB resume RA \`Initiating RA procedure\` -> gNB \`RRCResumeComplete received\`."
    echo "- [INACTIVE rrc_resume_request_to_connected_ms]: gNB \`RRCResumeRequest received\` -> gNB \`RRCResumeComplete received\`."
    echo
    echo "## Metrics"
    echo
    echo "| Mode | Metric | Start Marker | End Marker | Duration ms | Status | Smoke RC |"
    echo "|---|---|---|---|---:|---|---:|"
  } > "${SUMMARY_MD}"

  : > "${METRICS_CSV}"
  append_csv_row mode metric start_marker start_time_s end_marker end_time_s duration_ms status smoke_rc gnb_log ue_log console_log
}

main()
{
  init_outputs

  if [ "${RUN_EXPERIMENTS}" = "1" ]; then
    if [ ! -f "${SMOKE_SCRIPT}" ]; then
      echo "Smoke validation script not found: ${SMOKE_SCRIPT}" >&2
      exit 1
    fi

    if [ "${RUN_IDLE}" = "1" ]; then
      run_smoke_mode idle 0 0
    fi
    if [ "${RUN_INACTIVE}" = "1" ]; then
      run_smoke_mode inactive 1 1
    fi
  else
    if [ -z "${IDLE_GNB_LOG}" ] && [ -n "${INACTIVE_GNB_LOG}" ]; then
      IDLE_GNB_LOG="${INACTIVE_GNB_LOG}"
    fi
    if [ -z "${INACTIVE_GNB_LOG}" ] && [ -n "${IDLE_GNB_LOG}" ]; then
      INACTIVE_GNB_LOG="${IDLE_GNB_LOG}"
    fi
    if [ -z "${IDLE_GNB_LOG}" ] && [ -z "${INACTIVE_GNB_LOG}" ]; then
      IDLE_GNB_LOG=$(find_latest_gnb_log || true)
      INACTIVE_GNB_LOG="${IDLE_GNB_LOG}"
    fi
    if [ -z "${IDLE_UE_LOG}" ]; then
      IDLE_UE_LOG=$(ue_log_from_gnb_log "${IDLE_GNB_LOG}" "${FIRST_SAMPLE_UE}")
    fi
    if [ -z "${INACTIVE_UE_LOG}" ]; then
      INACTIVE_UE_LOG=$(ue_log_from_gnb_log "${INACTIVE_GNB_LOG}" "${FIRST_SAMPLE_UE}")
    fi
  fi

  if [ -n "${IDLE_GNB_LOG}" ]; then
    analyse_idle "${IDLE_GNB_LOG}" "${IDLE_UE_LOG}" "${IDLE_CONSOLE_LOG}" "${IDLE_SMOKE_RC}"
  else
    echo "[WARN] IDLE gNB log is missing; IDLE metrics will be absent" | tee -a "${SUMMARY_MD}"
  fi

  if [ -n "${INACTIVE_GNB_LOG}" ]; then
    analyse_inactive "${INACTIVE_GNB_LOG}" "${INACTIVE_UE_LOG}" "${INACTIVE_CONSOLE_LOG}" "${INACTIVE_SMOKE_RC}"
  else
    echo "[WARN] INACTIVE gNB log is missing; INACTIVE metrics will be absent" | tee -a "${SUMMARY_MD}"
  fi

  write_evidence_sections
  write_delta_section

  echo "[SUMMARY] run_id=${RUN_ID} idle_ra_ms=${IDLE_RA_TO_CONNECTED_MS} inactive_ra_ms=${INACTIVE_RA_TO_CONNECTED_MS} delta_ra_ms=$(delta_ms "${INACTIVE_RA_TO_CONNECTED_MS}" "${IDLE_RA_TO_CONNECTED_MS}") summary=${SUMMARY_MD} csv=${METRICS_CSV}"
}

main "$@"
