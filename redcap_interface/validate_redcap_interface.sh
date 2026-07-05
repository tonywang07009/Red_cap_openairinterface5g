#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/..")
LIB_DIR="${SCRIPT_DIR}/bash_library"
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

  if python3 - "${path}" <<'PY'; then
import ast
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
ast.parse(path.read_text(), filename=str(path))
PY
    echo "[OK] python syntax: ${path}"
  else
    echo "[FAIL] python syntax: ${path}" >&2
    failures=$((failures + 1))
  fi
}

for script in "${SCRIPT_DIR}"/*.sh "${SCRIPT_DIR}"/*.bash "${LIB_DIR}"/fc_*.sh "${LIB_DIR}"/fc_*.bash; do
  [ -f "${script}" ] || continue
  check_syntax "${script}"
done

check_file "${SCRIPT_DIR}/mmtc.menu.bash" "daily RFsim menu"
check_file "${SCRIPT_DIR}/mmtc.display.bash" "paper/demo display menu"
check_file "${SCRIPT_DIR}/mmtc.ment.bash" "legacy menu spelling alias"
check_file "${SCRIPT_DIR}/redcap_runtime_menu.sh" "legacy runtime menu shim"
check_file "${SCRIPT_DIR}/redcap_mmtc_smoke_validation.sh" "mMTC smoke runner shim"
check_file "${SCRIPT_DIR}/paper11_iperf_live_demo.sh" "PAPER-11 iperf demo runner shim"
check_file "${SCRIPT_DIR}/paper11_table3_peak_reproduction.sh" "PAPER-11 Table 3 peak runner shim"
check_file "${SCRIPT_DIR}/iperf_live_panel.py" "iperf live panel shim"
check_file "${SCRIPT_DIR}/redcap_mmtc_stage_scan.sh" "mMTC stage scan shim"
check_file "${SCRIPT_DIR}/redcap_runtime_host_validation.sh" "host validation runner shim"
check_file "${SCRIPT_DIR}/redcap_rrc_behavior_compare.bash" "RRC behavior comparator shim"
check_file "${SCRIPT_DIR}/generate_mmtc_cn_db_overlay.sh" "CN DB overlay generator shim"
check_file "${SCRIPT_DIR}/redcap_rebuild_local_oai_images.sh" "local image rebuild helper shim"
check_file "${SCRIPT_DIR}/redcap_inspect_gnb_image.sh" "gNB image inspector shim"
check_dir "${LIB_DIR}" "functional script library"
check_file "${LIB_DIR}/fc_runtime_menu_legacy.sh" "legacy runtime menu implementation"
check_file "${LIB_DIR}/fc_mmtc_smoke_validation.sh" "mMTC smoke implementation"
check_file "${LIB_DIR}/fc_mmtc_stage_scan.sh" "mMTC stage scan implementation"
check_file "${LIB_DIR}/fc_generate_mmtc_cn_db_overlay.sh" "CN DB overlay implementation"
check_file "${LIB_DIR}/fc_rebuild_local_oai_images.sh" "local image rebuild implementation"
check_file "${LIB_DIR}/fc_inspect_gnb_image.sh" "gNB image inspector implementation"
check_file "${LIB_DIR}/fc_runtime_host_validation.sh" "host validation implementation"
check_file "${LIB_DIR}/fc_runtime_case_matrix.sh" "runtime matrix implementation"
check_file "${LIB_DIR}/fc_runtime_e2_ab_test.sh" "E2 A/B implementation"
check_file "${LIB_DIR}/fc_send_ul_prb_control.sh" "UL PRB sender implementation"
check_file "${LIB_DIR}/fc_verify_ul_prb_control.sh" "UL PRB verifier implementation"
check_file "${LIB_DIR}/fc_paper08_fig9_chanmod_batch.sh" "PAPER-08 Fig. 9 implementation"
check_file "${LIB_DIR}/fc_paper11_iperf_live_demo.sh" "PAPER-11 live implementation"
check_file "${LIB_DIR}/fc_paper11_table3_peak_reproduction.sh" "PAPER-11 Table 3 implementation"
check_file "${LIB_DIR}/fc_iperf_live_panel.py" "iperf live panel implementation"
check_file "${LIB_DIR}/fc_rrc_behavior_compare.bash" "RRC behavior comparator implementation"

check_file "${REPO_ROOT}/ci-scripts/redcap_prepare_runtime_config.py" "runtime config Python helper"
check_file "${REPO_ROOT}/ci-scripts/redcap_runtime_summary.py" "runtime summary Python helper"
check_file "${REPO_ROOT}/ci-scripts/redcap_ul_prb_ctrl_xapp.c" "RedCap RC xApp source"
check_file "${REPO_ROOT}/openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.h" "RedCap xApp SDK header"
check_file "${REPO_ROOT}/openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.c" "RedCap xApp SDK source"
check_file "${REPO_ROOT}/openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.py" "RedCap xApp Python SDK"
check_file "${REPO_ROOT}/openair2/E3AP/sdk/redcap_dapp_sdk.h" "RedCap dApp SDK header"
check_file "${REPO_ROOT}/openair2/E3AP/sdk/redcap_dapp_sdk.c" "RedCap dApp SDK source"
check_file "${REPO_ROOT}/openair2/E3AP/sdk/redcap_dapp_sdk.py" "RedCap dApp Python SDK"
check_file "${REPO_ROOT}/agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/sdk/rapp/redcap_rapp_policy.h" "RedCap rApp C SDK header"
check_file "${REPO_ROOT}/agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/sdk/rapp/redcap_rapp_policy.c" "RedCap rApp C SDK source"
check_file "${REPO_ROOT}/agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/sdk/rapp/redcap_rapp_policy.schema.json" "RedCap rApp policy schema"
check_file "${REPO_ROOT}/agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/sdk/rapp/redcap_rapp_policy.py" "RedCap rApp Python SDK"
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
check_python_syntax "${LIB_DIR}/fc_iperf_live_panel.py"
check_python_syntax "${REPO_ROOT}/openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.py"
check_python_syntax "${REPO_ROOT}/openair2/E3AP/sdk/redcap_dapp_sdk.py"
check_python_syntax "${REPO_ROOT}/agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/sdk/rapp/redcap_rapp_policy.py"

tmp_sql=$(mktemp /tmp/redcap_mmtc_overlay.XXXXXX.sql)
tmp_yml=$(mktemp /tmp/redcap_mmtc_overlay.XXXXXX.yml)
bash "${LIB_DIR}/fc_generate_mmtc_cn_db_overlay.sh" 1 "${tmp_sql}" "${tmp_yml}" >/dev/null
check_file "${tmp_sql}" "generated one-UE SQL overlay smoke output"
check_file "${tmp_yml}" "generated one-UE compose overlay smoke output"
rm -f "${tmp_sql}" "${tmp_yml}"

if [ "${failures}" -ne 0 ]; then
  echo "[FAIL] RedCap interface validation found ${failures} issue(s)" >&2
  exit 1
fi

echo "[PASS] RedCap interface validation completed"
