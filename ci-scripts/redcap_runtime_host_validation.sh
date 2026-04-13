#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/..")
SCENARIO=${1:-container_5g_flexric_rfsim_redcap.xml}
TIMESTAMP=$(date +%F_%H-%M-%S)
EXPECTED_MODE=${REDCAP_EXPECTED_MODE:-}
GNB_CONFIG_PATH=${REDCAP_GNB_CONFIG_PATH:-}
E2_AGENT_MODE=${REDCAP_E2_AGENT_MODE:-enabled}
UE1_CONFIG_PATH=${NRUE_CONFIG_1_PATH:-${REDCAP_NRUE1_CONFIG_PATH:-}}
UE2_CONFIG_PATH=${NRUE_CONFIG_2_PATH:-${REDCAP_NRUE2_CONFIG_PATH:-}}
USE_LOCAL_OAI_IMAGES=${REDCAP_USE_LOCAL_OAI_IMAGES:-0}
REBUILD_LOCAL_OAI_IMAGES=${REDCAP_REBUILD_LOCAL_OAI_IMAGES:-0}
SERIALIZE_PING=${REDCAP_SERIALIZE_PING:-1}
REGISTRY_OVERRIDE=""
REGISTRY_OVERRIDE_SET=0
if [ "${REDCAP_REGISTRY+x}" = "x" ]; then
  REGISTRY_OVERRIDE="${REDCAP_REGISTRY}"
  REGISTRY_OVERRIDE_SET=1
fi
TAG_OVERRIDE=${REDCAP_TAG:-}
GNB_IMG_OVERRIDE=${REDCAP_GNB_IMG:-}
NRUE_IMG_OVERRIDE=${REDCAP_NRUE_IMG:-}
FLEXRIC_TAG_OVERRIDE=${REDCAP_FLEXRIC_TAG:-}
COMPOSE_ENV_FILE="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/.env"
FILE_SUFFIX=${EXPECTED_MODE:+_${EXPECTED_MODE}}
if [ "${E2_AGENT_MODE}" != "enabled" ]; then
  FILE_SUFFIX="${FILE_SUFFIX}_${E2_AGENT_MODE}"
fi
RUN_LOG="${REPO_ROOT}/test_log/compiler_logs/redcap_runtime_host${FILE_SUFFIX}_${TIMESTAMP}.log"
SUMMARY_MD="${REPO_ROOT}/test_log/report/redcap_runtime_host_summary${FILE_SUFFIX}_${TIMESTAMP}.md"
DEBUG_PREFIX="${REPO_ROOT}/test_log/compiler_logs/redcap_runtime_debug${FILE_SUFFIX}_${TIMESTAMP}"
RUNTIME_CONFIG_DIR="${REPO_ROOT}/test_log/runtime_configs"
COMPOSE_ENV_WRITTEN=0
COMPOSE_ENV_BACKUP=""

mkdir -p "${REPO_ROOT}/test_log/compiler_logs" "${REPO_ROOT}/test_log/report" "${RUNTIME_CONFIG_DIR}"

cd "${SCRIPT_DIR}"

cleanup() {
  if [ "${COMPOSE_ENV_WRITTEN}" -eq 1 ]; then
    if [ -n "${COMPOSE_ENV_BACKUP}" ] && [ -f "${COMPOSE_ENV_BACKUP}" ]; then
      mv "${COMPOSE_ENV_BACKUP}" "${COMPOSE_ENV_FILE}"
    else
      rm -f "${COMPOSE_ENV_FILE}"
    fi
  fi
}

trap cleanup EXIT

capture_debug_logs() {
  local container_name="$1"
  local output_file="$2"

  {
    echo "# container=${container_name}"
    echo "# collected_at=$(date --iso-8601=seconds)"
    docker logs "${container_name}" 2>&1 || echo "[WARN] unable to collect docker logs for ${container_name}"
  } > "${output_file}"
}

compose_env_lines=()
COMPOSE_ENV_DIRTY=0

upsert_compose_env_line() {
  local key="$1"
  local value="$2"
  local formatted="${key}=\"${value}\""
  local i
  for i in "${!compose_env_lines[@]}"; do
    if [[ "${compose_env_lines[$i]}" == "${key}="* ]]; then
      if [ "${compose_env_lines[$i]}" != "${formatted}" ]; then
        compose_env_lines[$i]="${formatted}"
        COMPOSE_ENV_DIRTY=1
      fi
      return
    fi
  done
  compose_env_lines+=("${formatted}")
  COMPOSE_ENV_DIRTY=1
}

if [ -f "${COMPOSE_ENV_FILE}" ]; then
  while IFS= read -r line; do
    [ -n "${line}" ] && compose_env_lines+=("${line}")
  done < "${COMPOSE_ENV_FILE}"
fi

if [ "${USE_LOCAL_OAI_IMAGES}" = "1" ]; then
  REGISTRY_OVERRIDE=""
  REGISTRY_OVERRIDE_SET=1
  [ -n "${TAG_OVERRIDE}" ] || TAG_OVERRIDE="latest"
  [ -n "${GNB_IMG_OVERRIDE}" ] || GNB_IMG_OVERRIDE="oai-gnb"
  [ -n "${NRUE_IMG_OVERRIDE}" ] || NRUE_IMG_OVERRIDE="oai-nr-ue"
fi

if [ "${USE_LOCAL_OAI_IMAGES}" = "1" ] && [ "${REBUILD_LOCAL_OAI_IMAGES}" = "1" ]; then
  echo "[INFO] Rebuilding local OAI images from workspace before runtime validation"
  "${SCRIPT_DIR}/redcap_rebuild_local_oai_images.sh"
fi

if [ "${E2_AGENT_MODE}" != "enabled" ]; then
  GENERATED_GNB_CONFIG="${RUNTIME_CONFIG_DIR}/gnb.redcap${FILE_SUFFIX}_${TIMESTAMP}.yaml"
  prepare_args=(
    --output "${GENERATED_GNB_CONFIG}"
    --e2-agent-mode "${E2_AGENT_MODE}"
  )
  if [ -n "${EXPECTED_MODE}" ]; then
    prepare_args+=(--mode "${EXPECTED_MODE}")
  fi
  if [ -n "${GNB_CONFIG_PATH}" ]; then
    prepare_args+=(--input "${GNB_CONFIG_PATH}")
  fi
  python3 "${SCRIPT_DIR}/redcap_prepare_runtime_config.py" "${prepare_args[@]}"
  GNB_CONFIG_PATH="${GENERATED_GNB_CONFIG}"
fi

if [ -n "${GNB_CONFIG_PATH}" ]; then
  upsert_compose_env_line "GNB_REDCAP_CONFIG" "${GNB_CONFIG_PATH}"
fi

if [ -n "${UE1_CONFIG_PATH}" ]; then
  upsert_compose_env_line "NRUE_CONFIG_1" "${UE1_CONFIG_PATH}"
fi

if [ -n "${UE2_CONFIG_PATH}" ]; then
  upsert_compose_env_line "NRUE_CONFIG_2" "${UE2_CONFIG_PATH}"
fi

if [ "${REGISTRY_OVERRIDE_SET}" -eq 1 ]; then
  upsert_compose_env_line "REGISTRY" "${REGISTRY_OVERRIDE}"
fi

if [ -n "${TAG_OVERRIDE}" ]; then
  upsert_compose_env_line "TAG" "${TAG_OVERRIDE}"
fi

if [ -n "${GNB_IMG_OVERRIDE}" ]; then
  upsert_compose_env_line "GNB_IMG" "${GNB_IMG_OVERRIDE}"
fi

if [ -n "${NRUE_IMG_OVERRIDE}" ]; then
  upsert_compose_env_line "NRUE_IMG" "${NRUE_IMG_OVERRIDE}"
fi

if [ -n "${FLEXRIC_TAG_OVERRIDE}" ]; then
  upsert_compose_env_line "FLEXRIC_TAG" "${FLEXRIC_TAG_OVERRIDE}"
fi

if [ "${COMPOSE_ENV_DIRTY}" -eq 1 ]; then
  if [ -f "${COMPOSE_ENV_FILE}" ]; then
    COMPOSE_ENV_BACKUP="${COMPOSE_ENV_FILE}.bak.${TIMESTAMP}"
    cp "${COMPOSE_ENV_FILE}" "${COMPOSE_ENV_BACKUP}"
  fi
  printf '%s\n' "${compose_env_lines[@]}" > "${COMPOSE_ENV_FILE}"
  COMPOSE_ENV_WRITTEN=1
fi

echo "[INFO] Runtime note: YAML/XML edits are picked up from this workspace, but C source changes require rebuilt container images."
if [ "${USE_LOCAL_OAI_IMAGES}" = "1" ]; then
  echo "[INFO] Local OAI image mode active: REGISTRY='' TAG='${TAG_OVERRIDE}' GNB_IMG='${GNB_IMG_OVERRIDE}' NRUE_IMG='${NRUE_IMG_OVERRIDE}'"
  echo "[INFO] These final images depend on [ran-build:latest]. If source patches changed, rebuild [ran-build:latest] before rerunning."
fi
if [ "${E2_AGENT_MODE}" != "enabled" ]; then
  echo "[INFO] E2 agent mode active: ${E2_AGENT_MODE}"
  echo "[INFO] Generated gNB config for A/B test: ${GNB_CONFIG_PATH}"
fi
if [ "${REGISTRY_OVERRIDE_SET}" -eq 1 ] || [ -n "${TAG_OVERRIDE}${GNB_IMG_OVERRIDE}${NRUE_IMG_OVERRIDE}${FLEXRIC_TAG_OVERRIDE}" ]; then
  echo "[INFO] Compose image override active: REGISTRY='${REGISTRY_OVERRIDE}' TAG='${TAG_OVERRIDE}' GNB_IMG='${GNB_IMG_OVERRIDE}' NRUE_IMG='${NRUE_IMG_OVERRIDE}' FLEXRIC_TAG='${FLEXRIC_TAG_OVERRIDE}'"
fi
if [ "${SERIALIZE_PING}" = "1" ]; then
  export OAI_CI_PING_SERIAL=1
  echo "[INFO] CI ping mode active: serial"
else
  unset OAI_CI_PING_SERIAL
  echo "[INFO] CI ping mode active: parallel"
fi

set +e
./run_locally.sh "${SCENARIO}" 2>&1 | tee "${RUN_LOG}"
RUN_RC=${PIPESTATUS[0]}
set -e

summary_args=(
  --scenario "${SCENARIO}"
  --run-log "${RUN_LOG}"
  --output "${SUMMARY_MD}"
)

if [ -n "${EXPECTED_MODE}" ]; then
  summary_args+=(--expected-mode "${EXPECTED_MODE}")
fi

if [ -n "${GNB_CONFIG_PATH}" ]; then
  summary_args+=(--config "${GNB_CONFIG_PATH}")
fi

python3 "${SCRIPT_DIR}/redcap_runtime_summary.py" "${summary_args[@]}"

if grep -Eq 'oai-ci/oai-(nr-ue|gnb):develop-[0-9a-f]+' "${RUN_LOG}"; then
  echo "[WARN] Prebuilt OAI image tag detected in run log. Local C patches in this repo are not present inside those containers until you rebuild and retag the images."
fi

if grep -Eq 'Cannot allocate all required PUCCH resources for max number of [0-9]+ UEs in BWP with [0-9]+ PRBs' "${RUN_LOG}"; then
  echo "[WARN] Detected the legacy gNB PUCCH budget assert. This usually means the running oai-gnb image does not include the workspace fix in openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c."
  echo "[WARN] Rebuild the local OAI images from this workspace and rerun with REDCAP_USE_LOCAL_OAI_IMAGES=1."
  echo "[WARN] Suggested commands:"
  echo "       bash ci-scripts/redcap_rebuild_local_oai_images.sh"
  echo "       bash ci-scripts/redcap_inspect_gnb_image.sh"
  echo "       REDCAP_USE_LOCAL_OAI_IMAGES=1 REDCAP_E2_AGENT_MODE=disabled bash ci-scripts/redcap_runtime_host_validation.sh"
fi

if [ "${RUN_RC}" -ne 0 ]; then
  docker ps -a > "${DEBUG_PREFIX}_docker_ps_a.log" 2>&1 || true
  capture_debug_logs "rfsim5g-oai-gnb_redcap" "${DEBUG_PREFIX}_gnb.log"
  capture_debug_logs "rfsim5g-oai-nr-ue1_redcap" "${DEBUG_PREFIX}_ue1.log"
  capture_debug_logs "rfsim5g-oai-nr-ue2_redcap" "${DEBUG_PREFIX}_ue2.log"
  capture_debug_logs "nearRT-RIC_redcap" "${DEBUG_PREFIX}_nearRT-RIC.log"
fi

echo "[Run Log] ${RUN_LOG}"
echo "[Summary] ${SUMMARY_MD}"

exit "${RUN_RC}"
