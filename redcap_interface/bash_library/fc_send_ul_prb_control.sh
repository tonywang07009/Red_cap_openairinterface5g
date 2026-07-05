#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
INTERFACE_DIR=$(realpath "${SCRIPT_DIR}/..")
REPO_ROOT=$(realpath "${INTERFACE_DIR}/..")
TIMESTAMP=$(date +%F_%H-%M-%S)

FLEXRIC_ROOT=${FLEXRIC_ROOT:-/home/tonywang/OAI/flexric}
FLEXRIC_BUILD=${FLEXRIC_BUILD:-${FLEXRIC_ROOT}/build-multi}
FLEXRIC_CONF=${FLEXRIC_CONF:-${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/conf/flexric.conf}
CONTROL_CONTRACT_FILE=${REDCAP_CONTROL_CONTRACT_FILE:-${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/control/redcap_control_contract.yaml}
POLICY_HOST_FILE=${REDCAP_POLICY_HOST_FILE:-${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/control/redcap_policy_case_b.yaml}
REFERENCE_PLUGIN_DIR=${REPO_ROOT}/redcap_library/library_runtime_probe/flexric_service_models
PLUGIN_DIR=${REDCAP_CTRL_PLUGIN_DIR:-${REPO_ROOT}/test_log/runtime_libs/flexric}
BIN_DIR=${REPO_ROOT}/test_log/runtime_bins
BUILD_LOG=${REPO_ROOT}/test_log/build_logs/redcap_ul_prb_ctrl_xapp_build_${TIMESTAMP}.log
RUN_LOG=${REPO_ROOT}/test_log/compiler_logs/redcap_rc_ctrl_xapp_${TIMESTAMP}.log
SRC=${REPO_ROOT}/ci-scripts/redcap_ul_prb_ctrl_xapp.c
SDK_SRC=${REPO_ROOT}/openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.c
BIN=${BIN_DIR}/redcap_ul_prb_ctrl_xapp
CC_BIN=${CC:-cc}
CAP_INPUT=${REDCAP_UL_PRB_CAP:-32}
DRY_RUN=${REDCAP_CTRL_DRY_RUN:-0}
BUILD_ONLY=${REDCAP_CTRL_BUILD_ONLY:-0}

mkdir -p "${REPO_ROOT}/test_log/build_logs" "${REPO_ROOT}/test_log/compiler_logs" "${BIN_DIR}" "${PLUGIN_DIR}"

normalize_integer()
{
  local raw="$1"
  if [[ "${raw}" =~ ^0[xX][0-9a-fA-F]+$ ]]; then
    printf '%u\n' "$((raw))"
    return 0
  fi

  if [[ "${raw}" =~ ^[0-9]+$ ]]; then
    printf '%s\n' "${raw}"
    return 0
  fi

  if [[ "${raw}" =~ ^[0-9a-fA-F]+$ ]]; then
    local upper="${raw^^}"
    printf '%u\n' "$((16#${upper}))"
    return 0
  fi

  return 1
}

extract_redcap_rnti()
{
  docker logs rfsim5g-oai-gnb_redcap 2>&1 | sed -nE 's/.*UE with RNTI ([0-9a-fA-F]{4}) is RedCap.*/0x\1/p' | tail -n 1
}

validate_redcap_ul_prb_contract()
{
  local contract_file="$1"
  local policy_file="$2"
  local cap_value="$3"

  python3 - "${contract_file}" "${policy_file}" "${cap_value}" <<'PY'
import pathlib
import re
import sys

contract_path = pathlib.Path(sys.argv[1])
policy_path = pathlib.Path(sys.argv[2])
cap = int(sys.argv[3])
param = "redcap_ul_prb_cap"

contract = contract_path.read_text(encoding="utf-8")
policy = policy_path.read_text(encoding="utf-8")

match = re.search(rf"(?ms)^  - name:\s*{re.escape(param)}\s*$([\s\S]*?)(?=^  - name:|\Z)", contract)
if match is None:
  raise SystemExit(f"[Contract][FAIL] {param} missing from {contract_path}")

block = match.group(1)
required = {
  "owner": "gnb_mac",
  "unit": "prb",
  "runtime_mutable": "true",
  "rollback": "restore_previous_value",
}
for field, expected in required.items():
  if not re.search(rf"(?m)^\s+{field}:\s*{re.escape(expected)}\s*$", block):
    raise SystemExit(f"[Contract][FAIL] {param} missing {field}: {expected}")

min_match = re.search(r"(?m)^\s+min:\s*(\d+)\s*$", block)
max_match = re.search(r"(?m)^\s+max:\s*(\d+)\s*$", block)
if min_match is None or max_match is None:
  raise SystemExit(f"[Contract][FAIL] {param} missing min/max")

min_value = int(min_match.group(1))
max_value = int(max_match.group(1))
if not min_value <= cap <= max_value:
  raise SystemExit(f"[Contract][FAIL] {param}={cap} outside [{min_value}, {max_value}]")

if not re.search(r"(?ms)^dynamic_control:\s*$(?:\n\s+[A-Za-z0-9_]+:\s+[^\n]+)*\n\s+enabled:\s+true\b", policy):
  raise SystemExit(f"[Policy][FAIL] dynamic_control.enabled is not true in {policy_path}")

if not re.search(rf"(?m)^\s+-\s+{re.escape(param)}\s*$", policy):
  raise SystemExit(f"[Policy][FAIL] {param} not allowed by {policy_path}")

print(f"[Contract][PASS] parameter={param} value={cap} range=[{min_value},{max_value}] policy={policy_path}")
PY
}

stage_plugin_libs()
{
  rm -f "${PLUGIN_DIR}"/lib*_sm.so
  mapfile -t sm_libs < <(find "${FLEXRIC_BUILD}/src/sm" -type f -name 'lib*_sm.so' | sort)
  if [[ ${#sm_libs[@]} -eq 0 ]]; then
    mapfile -t sm_libs < <(find "${REFERENCE_PLUGIN_DIR}" -maxdepth 1 \( -type f -o -type l \) -name 'lib*_sm.so' | sort)
    if [[ ${#sm_libs[@]} -eq 0 ]]; then
      echo "No FlexRIC service-model libraries found under ${FLEXRIC_BUILD}/src/sm or ${REFERENCE_PLUGIN_DIR}" >&2
      return 1
    fi
    echo "Using retained FlexRIC service-model libraries from ${REFERENCE_PLUGIN_DIR}" >&2
  fi

  for so_path in "${sm_libs[@]}"; do
    ln -sf "${so_path}" "${PLUGIN_DIR}/$(basename "${so_path}")"
  done
}

build_xapp()
{
  local compile_cmd=(
    "${CC_BIN}"
    -DASN
    -DE2AP_V3
    -DKPM_V3_00
    '-DSERVICE_MODEL_DIR_PATH="/"'
    -DSQLITE3_XAPP
    -I"${REPO_ROOT}"
    -I"${FLEXRIC_ROOT}/src"
    -g
    -fPIE
    -W
    -Wall
    -Wextra
    -std=gnu11
    "${SRC}"
    "${SDK_SRC}"
    -L"${FLEXRIC_BUILD}/src/xApp"
    -Wl,-rpath,"${FLEXRIC_BUILD}/src/xApp"
    -le42_xapp
    -pthread
    -lsctp
    -ldl
    -o
    "${BIN}"
  )

  {
    printf '[Compile] %q ' "${compile_cmd[@]}"
    printf '\n'
    "${compile_cmd[@]}"
  } 2>&1 | tee "${BUILD_LOG}"
}

stage_plugin_libs
build_xapp

echo "[Build Log] ${BUILD_LOG}"

if [[ "${BUILD_ONLY}" == "1" ]]; then
  exit 0
fi

if ! CAP_DEC=$(normalize_integer "${CAP_INPUT}"); then
  echo "Invalid REDCAP_UL_PRB_CAP value: ${CAP_INPUT}" >&2
  exit 1
fi

if ! CONTRACT_VALIDATION_OUTPUT=$(validate_redcap_ul_prb_contract "${CONTROL_CONTRACT_FILE}" "${POLICY_HOST_FILE}" "${CAP_DEC}" 2>&1); then
  echo "${CONTRACT_VALIDATION_OUTPUT}" >&2
  exit 1
fi

RAW_RNTI=${REDCAP_CTRL_RNTI:-}
if [[ -z "${RAW_RNTI}" ]]; then
  if [[ "${DRY_RUN}" == "1" ]]; then
    RAW_RNTI="0x1234"
  else
    RAW_RNTI=$(extract_redcap_rnti)
  fi
fi

if [[ -z "${RAW_RNTI}" ]]; then
  echo "Unable to resolve RedCap UE RNTI from gNB logs" >&2
  exit 1
fi

if ! RNTI_DEC=$(normalize_integer "${RAW_RNTI}"); then
  echo "Invalid REDCAP_CTRL_RNTI value: ${RAW_RNTI}" >&2
  exit 1
fi

UE_ID_RAW=${REDCAP_CTRL_UE_ID:-${RNTI_DEC}}
if ! UE_ID_DEC=$(normalize_integer "${UE_ID_RAW}"); then
  echo "Invalid REDCAP_CTRL_UE_ID value: ${UE_ID_RAW}" >&2
  exit 1
fi

{
  echo "${CONTRACT_VALIDATION_OUTPUT}"
  echo "# mode=$([[ "${DRY_RUN}" == "1" ]] && echo dry-run || echo live)"
  echo "# flexric_conf=${FLEXRIC_CONF}"
  echo "# plugin_dir=${PLUGIN_DIR}"
  echo "# control_contract=${CONTROL_CONTRACT_FILE}"
  echo "# policy_file=${POLICY_HOST_FILE}"
  echo "# contract_parameter=redcap_ul_prb_cap"
  echo "# raw_rnti=${RAW_RNTI}"
  echo "# rnti_dec=${RNTI_DEC}"
  echo "# ue_id_dec=${UE_ID_DEC}"
  echo "# max_ul_prb=${CAP_DEC}"
  LD_LIBRARY_PATH="${FLEXRIC_BUILD}/src/xApp:${LD_LIBRARY_PATH:-}" \
  REDCAP_CTRL_DRY_RUN="${DRY_RUN}" \
  REDCAP_CTRL_RNTI="${RNTI_DEC}" \
  REDCAP_CTRL_UE_ID="${UE_ID_DEC}" \
  REDCAP_CTRL_UL_PRB_CAP="${CAP_DEC}" \
  "${BIN}" \
    -c "${FLEXRIC_CONF}" \
    -p "${PLUGIN_DIR}/"
} 2>&1 | tee "${RUN_LOG}"

echo "[RC Control Log] ${RUN_LOG}"
