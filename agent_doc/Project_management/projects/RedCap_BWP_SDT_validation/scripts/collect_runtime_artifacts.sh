#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/redcap_runtime_common.sh"

MODE=""
LOG_DIR=""
SCENARIO=""
TAIL_LINES="${TAIL_LINES:-400}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="$2"
      shift 2
      ;;
    --log-dir)
      LOG_DIR="$2"
      shift 2
      ;;
    --scenario)
      SCENARIO="$2"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "${MODE}" || -z "${LOG_DIR}" || -z "${SCENARIO}" ]]; then
  echo "usage: $0 --mode <bwp|sdt> --log-dir <path> --scenario <name>" >&2
  exit 2
fi

case "${MODE}" in
  bwp|sdt)
    ;;
  *)
    echo "unsupported mode: ${MODE}" >&2
    exit 2
    ;;
esac

CONTAINER_LOG_DIR="${LOG_DIR}/container_logs"
FULL_LOG_DIR="${CONTAINER_LOG_DIR}/full"
mkdir -p "${FULL_LOG_DIR}"

redcap_collect_standard_runtime_logs "${LOG_DIR}" "${TAIL_LINES}"

redcap_extract_and_merge_runtime_metrics "${SCRIPT_DIR}" "${PROJECT_DIR}" "${MODE}" "${LOG_DIR}" "${SCENARIO}"

echo "[${MODE}] collected logs: ${CONTAINER_LOG_DIR}"
