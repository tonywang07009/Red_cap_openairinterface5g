#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${PROJECT_DIR}/../../../.." && pwd)"
COMPOSE_DIR="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap"
CONFIG_FILE="${PROJECT_DIR}/configs/BWP_local_matrix.yaml"
RUN_MODE="${1:---dry-run}"
RUN_ID="${RUN_ID:-$(date +%Y%m%d_%H%M%S)}"
LOG_DIR="${REPO_ROOT}/test_log/redcap_bwp_sdt_validation/${RUN_ID}_bwp"
SERVICES="${SERVICES:-nearRT-RIC oai-gnb oai-nr-ue2 xapp-kpm-rc}"

case "${RUN_MODE}" in
  --dry-run|--run)
    ;;
  *)
    echo "usage: $0 [--dry-run|--run]" >&2
    exit 2
    ;;
esac

mkdir -p "${LOG_DIR}"

export MMTC_REDCAP_ENABLE="${MMTC_REDCAP_ENABLE:-1}"
export MMTC_REDCAP_NUM_RX="${MMTC_REDCAP_NUM_RX:-1}"
export MMTC_REDCAP_HALF_DUPLEX="${MMTC_REDCAP_HALF_DUPLEX:-1}"
export MMTC_N_RB_DL="${MMTC_N_RB_DL:-106}"
export MMTC_NUMEROLOGY="${MMTC_NUMEROLOGY:-1}"
export MMTC_RF_FREQ="${MMTC_RF_FREQ:-3630360000}"
export MMTC_SSB_START="${MMTC_SSB_START:-144}"
export MMTC_DRX_PROFILE="${MMTC_DRX_PROFILE:-balanced}"

cat > "${LOG_DIR}/run_manifest.txt" <<EOF
experiment=BWP_switching_with_DRX
config=${CONFIG_FILE}
compose_root=${COMPOSE_DIR}
run_mode=${RUN_MODE}
services=${SERVICES}
MMTC_REDCAP_ENABLE=${MMTC_REDCAP_ENABLE}
MMTC_REDCAP_NUM_RX=${MMTC_REDCAP_NUM_RX}
MMTC_REDCAP_HALF_DUPLEX=${MMTC_REDCAP_HALF_DUPLEX}
MMTC_N_RB_DL=${MMTC_N_RB_DL}
MMTC_NUMEROLOGY=${MMTC_NUMEROLOGY}
MMTC_RF_FREQ=${MMTC_RF_FREQ}
MMTC_SSB_START=${MMTC_SSB_START}
MMTC_DRX_PROFILE=${MMTC_DRX_PROFILE}
note=BWP timer and switch-delay values are recorded in the YAML matrix and still need OAI runtime wiring.
EOF

echo "[BWP] manifest: ${LOG_DIR}/run_manifest.txt"
echo "[BWP] config: ${CONFIG_FILE}"
echo "[BWP] services: ${SERVICES}"

if [[ "${RUN_MODE}" == "--dry-run" ]]; then
  echo "[BWP] dry-run only. Use --run to start docker compose."
  exit 0
fi

cd "${COMPOSE_DIR}"
read -r -a SERVICE_ARGS <<< "${SERVICES}"
docker compose -f docker-compose.yml -f docker-compose.mmtc.yml up -d "${SERVICE_ARGS[@]}" 2>&1 | tee "${LOG_DIR}/docker_compose_up.log"
docker compose -f docker-compose.yml -f docker-compose.mmtc.yml ps 2>&1 | tee "${LOG_DIR}/docker_compose_ps.log"
