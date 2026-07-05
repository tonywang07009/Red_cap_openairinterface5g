#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_MODE="${1:---dry-run}"

case "${RUN_MODE}" in
  --dry-run|--run)
    ;;
  *)
    echo "usage: $0 [--dry-run|--run]" >&2
    exit 2
    ;;
esac

LOAD_PROFILES="${BWP_LOAD_PROFILES:-low_load high_load}"
INACTIVITY_TIMERS_MS="${BWP_INACTIVITY_TIMERS_MS:-8 80}"
SWITCH_DELAYS_MS="${BWP_SWITCH_DELAYS_MS:-1 3}"
BASE_RUN_ID="${RUN_ID:-$(date +%Y%m%d_%H%M%S)_bwp_matrix}"
BWP_MATRIX_TRIGGER_SEQUENCE="${BWP_MATRIX_TRIGGER_SEQUENCE:-1 0}"
BWP_MATRIX_STOP_AFTER_RUN="${BWP_MATRIX_STOP_AFTER_RUN:-1}"
BWP_MATRIX_RUN_WAIT_SECONDS="${BWP_MATRIX_RUN_WAIT_SECONDS:-45}"
BWP_MATRIX_FORCE_RECREATE="${BWP_MATRIX_FORCE_RECREATE:-1}"
MATRIX_RUNS=0
MATRIX_FAILURES=0

for load_profile in ${LOAD_PROFILES}; do
  for timer_ms in ${INACTIVITY_TIMERS_MS}; do
    for switch_delay_ms in ${SWITCH_DELAYS_MS}; do
      scenario="${load_profile}_bwp_${timer_ms}ms_${switch_delay_ms}ms"
      scenario_run_id="${BASE_RUN_ID}_${scenario}"
      echo "[BWP matrix] scenario=${scenario} mode=${RUN_MODE}"
      if [[ "${RUN_MODE}" == "--dry-run" ]]; then
        echo "RUN_ID=${scenario_run_id} RUNTIME_SCENARIO=${scenario} MMTC_BWP_TRAFFIC_PROFILE=${load_profile} MMTC_BWP_INACTIVITY_TIMER_MS=${timer_ms} MMTC_BWP_SWITCH_DELAY_MS=${switch_delay_ms} BWP_TRIGGER_SEQUENCE='${BWP_MATRIX_TRIGGER_SEQUENCE}' STOP_AFTER_RUN=${BWP_MATRIX_STOP_AFTER_RUN} RUN_WAIT_SECONDS=${BWP_MATRIX_RUN_WAIT_SECONDS} REDCAP_COMPOSE_FORCE_RECREATE=${BWP_MATRIX_FORCE_RECREATE} ${SCRIPT_DIR}/run_bwp_validation.sh --run"
        continue
      fi
      set +e
      RUN_ID="${scenario_run_id}" \
      RUNTIME_SCENARIO="${scenario}" \
      MMTC_BWP_TRAFFIC_PROFILE="${load_profile}" \
      MMTC_BWP_INACTIVITY_TIMER_MS="${timer_ms}" \
      MMTC_BWP_SWITCH_DELAY_MS="${switch_delay_ms}" \
      BWP_TRIGGER_SEQUENCE="${BWP_MATRIX_TRIGGER_SEQUENCE}" \
      STOP_AFTER_RUN="${BWP_MATRIX_STOP_AFTER_RUN}" \
      RUN_WAIT_SECONDS="${BWP_MATRIX_RUN_WAIT_SECONDS}" \
      REDCAP_COMPOSE_FORCE_RECREATE="${BWP_MATRIX_FORCE_RECREATE}" \
      "${SCRIPT_DIR}/run_bwp_validation.sh" --run
      scenario_rc="$?"
      set -e
      MATRIX_RUNS=$((MATRIX_RUNS + 1))
      if [[ "${scenario_rc}" -ne 0 ]]; then
        MATRIX_FAILURES=$((MATRIX_FAILURES + 1))
        echo "[BWP matrix][WARN] scenario=${scenario} runner_rc=${scenario_rc}; metrics were extracted if logs were available"
      fi
    done
  done
done

if [[ "${RUN_MODE}" == "--run" ]]; then
  echo "[BWP matrix] completed runs=${MATRIX_RUNS} runner_failures=${MATRIX_FAILURES}"
  if [[ "${MATRIX_FAILURES}" -ne 0 ]]; then
    exit 1
  fi
fi
