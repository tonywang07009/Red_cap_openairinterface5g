#!/usr/bin/env bash

set -u

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/..")
PROJECT_DIR="${REPO_ROOT}/agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1"
RUNNER="${PROJECT_DIR}/analysis/scripts/p08_fig9_udp_snr_sweep.py"
SMOKE="${REPO_ROOT}/redcap_interface/redcap_mmtc_smoke_validation.sh"
TIMESTAMP=${P08_TIMESTAMP:-$(date +%F_%H-%M-%S)}
CHANNEL_MODELS_RAW=${P08_CHANNEL_MODELS:-"AWGN Rayleigh1 Rayleigh8 Rayleigh1_corr Rayleigh1_anticorr Rice1 Rice8 TDL_A"}
SNR_NOISE_PAIRS=${P08_SNR_NOISE_PAIRS:-"30:-80,20:-65,10:-50,0:-40"}
DURATION=${P08_DURATION:-15}
OFFERED_RATE=${P08_OFFERED_RATE:-90M}
PLOSS_DB=${P08_PLOSS_DB:-0}
TDL_DS_TDL=${P08_TDL_DS_TDL:-0.00000003}
BLOCKED_CSV="${PROJECT_DIR}/analysis/data/paper08_fig9_udp_snr_blocked_${TIMESTAMP}.csv"

CSV_PATHS=()
FAILURES=0

mkdir -p "${PROJECT_DIR}/analysis/data"
printf 'channel_model,stage,status,evidence_path,limitation_note\n' > "${BLOCKED_CSV}"

append_blocked_model()
{
  local model="$1"
  local stage="$2"
  local status="$3"
  local evidence="$4"
  local note="$5"

  printf '%s,%s,%s,%s,%s\n' "${model}" "${stage}" "${status}" "${evidence}" "${note}" >> "${BLOCKED_CSV}"
}

for model in ${CHANNEL_MODELS_RAW}; do
  run_id="paper08_fig9_udp_snr_${model}_${TIMESTAMP}"
  echo "[INFO] PAPER-08 Fig.9 channel model: ${model}"

  if ! GNB_REDCAP_CONFIG="${REPO_ROOT}/ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml" \
    MMTC_N_RB_DL=106 \
    MMTC_RF_FREQ=3630360000 \
    MMTC_SSB_START=144 \
    MMTC_TOTAL_UES=29 \
    MMTC_SAMPLE_UES=1 \
    MMTC_IPERF_ENABLE=0 \
    MMTC_FORWARD_PING_MODE=parallel \
    MMTC_RUN_REVERSE_PING=0 \
    MMTC_PUCCH_COMMON_FALLBACK_BWP0=1 \
    MMTC_REDCAP_ENABLE=1 \
    MMTC_REDCAP_NUM_RX=1 \
    MMTC_REDCAP_HALF_DUPLEX=1 \
    MMTC_GNB_EXTRA_OPTIONS="" \
    MMTC_UE_EXTRA_OPTIONS="--rfsimulator.options chanmod" \
    MMTC_CHANMOD_DL_TYPE="${model}" \
    MMTC_CHANMOD_DL_PLOSS_DB="${PLOSS_DB}" \
    MMTC_CHANMOD_DL_NOISE_DB=-80 \
    MMTC_CHANMOD_DL_DS_TDL="${TDL_DS_TDL}" \
    bash "${SMOKE}"; then
    echo "[WARN] Smoke setup failed for model=${model}"
    append_blocked_model \
      "${model}" \
      "smoke_setup" \
      "blocked" \
      "test_log/compiler_logs/" \
      "UE attach/tunnel did not become ready with startup channel model"
    FAILURES=$((FAILURES + 1))
    continue
  fi

  if ! python3 -B "${RUNNER}" \
    --channel-models "${model}" \
    --skip-setmodel \
    --snr-noise-pairs "${SNR_NOISE_PAIRS}" \
    --duration "${DURATION}" \
    --offered-rate "${OFFERED_RATE}" \
    --ploss-db "${PLOSS_DB}" \
    --run-id "${run_id}"; then
    echo "[WARN] Sweep failed for model=${model}"
    append_blocked_model \
      "${model}" \
      "measurement_sweep" \
      "partial" \
      "analysis/data/${run_id}.csv" \
      "one or more iperf measurement rows returned non-zero"
    FAILURES=$((FAILURES + 1))
  fi

  csv_path="${PROJECT_DIR}/analysis/data/${run_id}.csv"
  if [ -f "${csv_path}" ]; then
    CSV_PATHS+=("${csv_path}")
  fi
done

if [ "${#CSV_PATHS[@]}" -gt 0 ]; then
  python3 -B "${RUNNER}" \
    --run-id "paper08_fig9_udp_snr_combined_${TIMESTAMP}" \
    --blocked-models-file "${BLOCKED_CSV}" \
    --combine-csvs "${CSV_PATHS[@]}"
else
  echo "[WARN] No CSV files produced; skip combined plot"
  FAILURES=$((FAILURES + 1))
fi

echo "[SUMMARY] channel_models='${CHANNEL_MODELS_RAW}' csv_count=${#CSV_PATHS[@]} failures=${FAILURES}"
exit "${FAILURES}"
