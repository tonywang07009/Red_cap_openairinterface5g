#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/..")
failures=0

check_file()
{
  local path="$1"
  local label="$2"

  if [ -f "${path}" ]; then
    echo "[OK] ${label}: ${path}"
  else
    echo "[FAIL] missing ${label}: ${path}" >&2
    failures=$((failures + 1))
  fi
}

check_dir()
{
  local path="$1"
  local label="$2"

  if [ -d "${path}" ]; then
    echo "[OK] ${label}: ${path}"
  else
    echo "[FAIL] missing ${label}: ${path}" >&2
    failures=$((failures + 1))
  fi
}

check_syntax()
{
  local path="$1"

  if bash -n "${path}"; then
    echo "[OK] syntax: ${path}"
  else
    echo "[FAIL] syntax: ${path}" >&2
    failures=$((failures + 1))
  fi
}

check_python_syntax()
{
  local path="$1"

  if python3 -m py_compile "${path}"; then
    echo "[OK] python syntax: ${path}"
  else
    echo "[FAIL] python syntax: ${path}" >&2
    failures=$((failures + 1))
  fi
}

for script in "${SCRIPT_DIR}"/*.sh "${SCRIPT_DIR}"/*.bash; do
  check_syntax "${script}"
done

check_file "${SCRIPT_DIR}/redcap_runtime_menu.sh" "runtime menu"
check_file "${SCRIPT_DIR}/mmtc.menu.bash" "runtime menu launcher"
check_file "${SCRIPT_DIR}/mmtc.ment.bash" "runtime menu launcher alias"
check_file "${SCRIPT_DIR}/redcap_mmtc_smoke_validation.sh" "mMTC smoke runner"
check_file "${SCRIPT_DIR}/paper11_iperf_live_demo.sh" "PAPER-11 iperf demo runner"
check_file "${SCRIPT_DIR}/paper11_table3_peak_reproduction.sh" "PAPER-11 Table 3 peak runner"
check_file "${SCRIPT_DIR}/iperf_live_panel.py" "iperf live panel"
check_file "${SCRIPT_DIR}/redcap_mmtc_stage_scan.sh" "mMTC stage scan"
check_file "${SCRIPT_DIR}/redcap_runtime_host_validation.sh" "host validation runner"
check_file "${SCRIPT_DIR}/generate_mmtc_cn_db_overlay.sh" "CN DB overlay generator"
check_file "${SCRIPT_DIR}/redcap_rebuild_local_oai_images.sh" "local image rebuild helper"
check_file "${SCRIPT_DIR}/redcap_inspect_gnb_image.sh" "gNB image inspector"

check_file "${REPO_ROOT}/ci-scripts/redcap_prepare_runtime_config.py" "runtime config Python helper"
check_file "${REPO_ROOT}/ci-scripts/redcap_runtime_summary.py" "runtime summary Python helper"
check_file "${REPO_ROOT}/ci-scripts/redcap_ul_prb_ctrl_xapp.c" "RedCap RC xApp source"
check_file "${REPO_ROOT}/ci-scripts/run_locally.sh" "OAI local CI runner"

check_file "${REPO_ROOT}/ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml" "106PRB gNB config"
check_file "${REPO_ROOT}/ci-scripts/conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml" "51PRB gNB config"
check_file "${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml" "base RFsim compose"
check_file "${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml" "mMTC compose overlay"
check_file "${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh" "mMTC overlay generator"
check_file "${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/conf/flexric.conf" "FlexRIC config"

check_file "${REPO_ROOT}/redcap_library/library_gnb_config/gnb_redcap_mmtc_case_b_final.yaml" "default curated gNB config"
check_dir "${REPO_ROOT}/redcap_library/library_runtime_probe/flexric_service_models" "retained FlexRIC service-model directory"
check_dir "${REPO_ROOT}/redcap_doc/evluation_recover" "evaluation reproduction recovery manuals"
check_dir "${REPO_ROOT}/test_log" "temporary log root"

check_python_syntax "${SCRIPT_DIR}/iperf_live_panel.py"

tmp_sql=$(mktemp /tmp/redcap_mmtc_overlay.XXXXXX.sql)
tmp_yml=$(mktemp /tmp/redcap_mmtc_overlay.XXXXXX.yml)
bash "${SCRIPT_DIR}/generate_mmtc_cn_db_overlay.sh" 1 "${tmp_sql}" "${tmp_yml}" >/dev/null
check_file "${tmp_sql}" "generated one-UE SQL overlay smoke output"
check_file "${tmp_yml}" "generated one-UE compose overlay smoke output"
rm -f "${tmp_sql}" "${tmp_yml}"

if [ "${failures}" -ne 0 ]; then
  echo "[FAIL] RedCap interface validation found ${failures} issue(s)" >&2
  exit 1
fi

echo "[PASS] RedCap interface validation completed"
