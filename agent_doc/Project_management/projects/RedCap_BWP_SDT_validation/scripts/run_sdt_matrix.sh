#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUN_MODE="${1:---dry-run}"

case "${RUN_MODE}" in
  --dry-run|--run)
    ;;
  *)
    echo "usage: $0 [--dry-run|--run]" >&2
    exit 2
    ;;
esac

SCENARIOS="${SDT_SCENARIOS:-4_step_ra 2_step_ra 4_step_sdt 2_step_sdt 4_step_ra_slot10 2_step_ra_slot10 4_step_sdt_slot10 2_step_sdt_slot10 4_step_ra_lambda_dp_5 2_step_ra_lambda_dp_5 4_step_sdt_lambda_dp_5 2_step_sdt_lambda_dp_5}"
SDT_REPEATS="${SDT_REPEATS:-3}"
BASE_RUN_ID="${RUN_ID:-$(date +%Y%m%d_%H%M%S)_sdt_matrix}"
MATRIX_RUNS=0
MATRIX_FAILURES=0

scenario_access_steps()
{
  case "$1" in
    2_step_*)
      echo 2
      ;;
    *)
      echo 4
      ;;
  esac
}

scenario_mode()
{
  case "$1" in
    *_sdt*)
      echo sdt
      ;;
    *)
      echo ra
      ;;
  esac
}

for scenario in ${SCENARIOS}; do
  mode="$(scenario_mode "${scenario}")"
  access_steps="$(scenario_access_steps "${scenario}")"
  for repeat in $(seq 1 "${SDT_REPEATS}"); do
    scenario_run_id="${BASE_RUN_ID}_${scenario}_r${repeat}"
    echo "[SDT matrix] scenario=${scenario} repeat=${repeat}/${SDT_REPEATS} mode=${mode} access_steps=${access_steps} run_mode=${RUN_MODE}"
    if [[ "${RUN_MODE}" == "--dry-run" ]]; then
      echo "RUN_ID=${scenario_run_id} RUNTIME_SCENARIO=${scenario} MMTC_RA_ACCESS_STEPS=${access_steps} MMTC_RRC_INACTIVE_GATE2_RESUME_TRIGGER=$([[ "${mode}" == "ra" ]] && echo 1 || echo 0) MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=$([[ "${mode}" == "sdt" ]] && echo 1 || echo 0) MMTC_SDT_MENU_SUBCOMMAND=smoke ${SCRIPT_DIR}/run_sdt_validation.sh --run"
      continue
    fi
    set +e
    RUN_ID="${scenario_run_id}" \
    RUNTIME_SCENARIO="${scenario}" \
    MMTC_RA_ACCESS_STEPS="${access_steps}" \
    MMTC_RRC_INACTIVE_GATE2_RESUME_TRIGGER="$([[ "${mode}" == "ra" ]] && echo 1 || echo 0)" \
    MMTC_RRC_INACTIVE_GATE3_CG_CONFIG="$([[ "${mode}" == "sdt" ]] && echo 1 || echo 0)" \
    MMTC_SDT_MENU_SUBCOMMAND=smoke \
    "${SCRIPT_DIR}/run_sdt_validation.sh" --run
    scenario_rc="$?"
    set -e
    MATRIX_RUNS=$((MATRIX_RUNS + 1))
    if [[ "${scenario_rc}" -ne 0 ]]; then
      MATRIX_FAILURES=$((MATRIX_FAILURES + 1))
      echo "[SDT matrix][WARN] scenario=${scenario} repeat=${repeat}/${SDT_REPEATS} runner_rc=${scenario_rc}; metrics were extracted if logs were available"
    fi
  done
done

if [[ "${RUN_MODE}" == "--run" ]]; then
  "${PYTHON:-python3}" "${SCRIPT_DIR}/aggregate_sdt_success.py" \
    --runtime-glob "test_log/redcap_bwp_sdt_validation/${BASE_RUN_ID}_*_sdt/sdt_runtime_metrics.csv" \
    --target "${PROJECT_DIR}/exp_result/SDT_results.csv"
  echo "[SDT matrix] completed runs=${MATRIX_RUNS} runner_failures=${MATRIX_FAILURES}"
  if [[ "${MATRIX_FAILURES}" -ne 0 ]]; then
    exit 1
  fi
fi
