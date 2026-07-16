#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/..")
LIB_DIR="${SCRIPT_DIR}/bash_library"
MAIN_MENU="${REPO_ROOT}/mmtc.menu.bash"
LEGACY_MAIN_MENU="${SCRIPT_DIR}/mmtc.menu.bash"
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

check_command_success()
{
  local label="$1"
  shift

  if "$@" >/dev/null 2>&1; then
    echo "[OK] ${label}"
  else
    echo "[FAIL] ${label}" >&2
    failures=$((failures + 1))
  fi
}

check_command_failure()
{
  local label="$1"
  shift

  if "$@" >/dev/null 2>&1; then
    echo "[FAIL] ${label}: command unexpectedly succeeded" >&2
    failures=$((failures + 1))
  else
    echo "[OK] ${label}"
  fi
}

check_bilingual_help()
{
  local path="$1"
  local label="$2"
  local output

  if ! output=$(bash "${path}" --help 2>&1); then
    echo "[FAIL] ${label}: --help returned non-zero" >&2
    failures=$((failures + 1))
    return
  fi

  if [[ "${output}" == *"用法"* ]] && [[ "${output}" == *"Usage"* ]] && [[ "${output}" == *"MMTC_ACTIVE_UES"* ]]; then
    echo "[OK] bilingual help: ${path}"
  else
    echo "[FAIL] ${label}: bilingual help content is incomplete" >&2
    failures=$((failures + 1))
  fi
}

check_installer_help()
{
  local output
  if output=$(bash "${LIB_DIR}/fc_install_redcap.sh" --help 2>&1) \
    && [[ "${output}" == *"用法"* ]] \
    && [[ "${output}" == *"Usage"* ]] \
    && [[ "${output}" == *"install --check"* ]] \
    && [[ "${output}" == *"1 UE"* ]]; then
    echo "[OK] bilingual installer help"
  else
    echo "[FAIL] bilingual installer help is incomplete" >&2
    failures=$((failures + 1))
  fi
}

for script in "${SCRIPT_DIR}"/*.sh "${SCRIPT_DIR}"/*.bash "${LIB_DIR}"/fc_*.sh "${LIB_DIR}"/fc_*.bash; do
  [ -f "${script}" ] || continue
  check_syntax "${script}"
done

check_syntax "${MAIN_MENU}"
check_file "${MAIN_MENU}" "root daily RFsim menu"
check_file "${LEGACY_MAIN_MENU}" "legacy daily RFsim menu shim"
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
check_file "${LIB_DIR}/fc_install_redcap.sh" "interactive installer implementation"
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
check_file "${REPO_ROOT}/oai-cn5g/docker-compose.yaml" "repository-owned CN5G compose"
check_file "${REPO_ROOT}/oai-cn5g/conf/config.yaml" "repository-owned CN5G config"
check_file "${REPO_ROOT}/oai-cn5g/database/oai_db.sql" "repository-owned CN5G database baseline"
check_file "${REPO_ROOT}/oai-cn5g/database/oai_db_mmtc_56.sql" "fixed 56-UE CN5G seed"
check_file "${REPO_ROOT}/oai-cn5g/healthscripts/mysql-healthcheck.sh" "repository-owned CN5G healthcheck"
check_file "${LIB_DIR}/generate_mmtc_overlay.sh" "mMTC overlay generator"
check_file "${LIB_DIR}/ue_mmtc_entrypoint.sh" "mMTC UE entrypoint"
check_file "${SCRIPT_DIR}/control/redcap_control_contract.yaml" "RedCap control contract"
check_file "${SCRIPT_DIR}/control/redcap_policy_case_a.yaml" "RedCap Case A policy"
check_file "${SCRIPT_DIR}/control/redcap_policy_case_b.yaml" "RedCap Case B policy"
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
bash "${LIB_DIR}/fc_generate_mmtc_cn_db_overlay.sh" 56 "${tmp_sql}" "${tmp_yml}" >/dev/null
check_file "${tmp_sql}" "generated 56-UE SQL overlay smoke output"
check_file "${tmp_yml}" "generated 56-UE compose overlay smoke output"
if cmp -s "${tmp_sql}" "${REPO_ROOT}/oai-cn5g/database/oai_db_mmtc_56.sql"; then
  echo "[OK] fixed 56-UE seed matches generator output"
else
  echo "[FAIL] fixed 56-UE seed differs from generator output" >&2
  failures=$((failures + 1))
fi
rm -f "${tmp_sql}" "${tmp_yml}"

check_bilingual_help "${MAIN_MENU}" "daily RFsim menu help"
check_bilingual_help "${LEGACY_MAIN_MENU}" "legacy daily RFsim menu shim help"
check_bilingual_help "${LIB_DIR}/fc_mmtc_smoke_validation.sh" "mMTC smoke help"
check_installer_help
check_command_success "menu installer help route" bash "${MAIN_MENU}" install --help
check_command_failure "menu rejects unknown option" bash "${MAIN_MENU}" --unknown
check_command_failure "smoke rejects unknown option" bash "${LIB_DIR}/fc_mmtc_smoke_validation.sh" --unknown
check_command_failure "installer rejects unknown option" bash "${LIB_DIR}/fc_install_redcap.sh" --unknown
check_command_success "installer initial confirmation decline" bash -c "printf 'n\\n' | bash '$LIB_DIR/fc_install_redcap.sh'"
check_command_failure "installer rejects a concurrent interactive run" flock "${TMPDIR:-/tmp}/redcap-interactive-install.lock" bash -c "printf 'y\\n' | bash '$LIB_DIR/fc_install_redcap.sh'"

check_command_success "installer accepts 40 GiB minimum boundary" env REDCAP_INSTALL_MIN_FREE_GB=40 bash "${LIB_DIR}/fc_install_redcap.sh" --help
check_command_failure "installer rejects 39 GiB minimum boundary" env REDCAP_INSTALL_MIN_FREE_GB=39 bash "${LIB_DIR}/fc_install_redcap.sh" --help
check_command_failure "installer rejects negative disk threshold" env REDCAP_INSTALL_MIN_FREE_GB=-1 bash "${LIB_DIR}/fc_install_redcap.sh" --help
check_command_failure "installer rejects non-numeric disk threshold" env REDCAP_INSTALL_MIN_FREE_GB=invalid bash "${LIB_DIR}/fc_install_redcap.sh" --help

missing_uv_output=$(PATH=/usr/bin:/bin bash "${LIB_DIR}/fc_install_redcap.sh" --check 2>&1 || true)
if [[ "${missing_uv_output}" == *"uv is not installed"* ]]; then
  echo "[OK] installer reports missing uv"
else
  echo "[FAIL] installer did not report missing uv" >&2
  failures=$((failures + 1))
fi

check_command_failure "installer rejects a stale uv lock" bash -c '
  source "$1"
  docker() { return 0; }
  uv() { [ "${1:-}" != "lock" ]; }
  check_host interactive
' _ "${LIB_DIR}/fc_install_redcap.sh"

check_command_failure "installer reports missing Docker API access" bash -c '
  source "$1"
  docker() { [ "${1:-}" != "info" ]; }
  uv() { return 0; }
  check_host interactive
' _ "${LIB_DIR}/fc_install_redcap.sh"

if bash -c 'source "$1"; build_services | rg -qx nearRT-RIC' _ "${LIB_DIR}/fc_install_redcap.sh"; then
  echo "[OK] installer detects Compose-declared local FlexRIC build"
else
  echo "[FAIL] installer did not detect the Compose-declared local build" >&2
  failures=$((failures + 1))
fi

valid_summary=$(mktemp /tmp/redcap_install_summary.XXXXXX.log)
invalid_summary=$(mktemp /tmp/redcap_install_summary.XXXXXX.log)
printf '%s\n' '[SUMMARY] sample=1 active=1 running=1 attach=1 pdu=1 tun=1 forward_ping_ok=1 reverse_ping_ok=0 iperf_ok=0 gnb_restart=0 failures=0 log=x' > "${valid_summary}"
printf '%s\n' '[SUMMARY] sample=1 active=1 running=1 attach=1 pdu=1 tun=0 forward_ping_ok=0 reverse_ping_ok=0 iperf_ok=0 gnb_restart=0 failures=1 log=x' > "${invalid_summary}"
check_command_success "installer accepts complete 1 UE markers" bash -c 'source "$1"; smoke_summary_passes "$2"' _ "${LIB_DIR}/fc_install_redcap.sh" "${valid_summary}"
check_command_failure "installer rejects incomplete 1 UE markers" bash -c 'source "$1"; smoke_summary_passes "$2"' _ "${LIB_DIR}/fc_install_redcap.sh" "${invalid_summary}"
rm -f "${valid_summary}" "${invalid_summary}"

read_only_id="validate_read_only_$$"
read_only_profile="${REPO_ROOT}/test_log/runtime_configs/${read_only_id}.profile.env"
read_only_overlay="${REPO_ROOT}/test_log/runtime_configs/${read_only_id}_overlay.yml"
rm -f "${read_only_profile}" "${read_only_overlay}"
check_command_success "side-effect-free project introduction" env MMTC_RUN_ID="${read_only_id}" bash "${MAIN_MENU}" intro
check_command_success "side-effect-free performance evidence" env MMTC_RUN_ID="${read_only_id}" bash "${MAIN_MENU}" performance
if [ -e "${read_only_profile}" ] || [ -e "${read_only_overlay}" ]; then
  echo "[FAIL] read-only menu route created a runtime file" >&2
  failures=$((failures + 1))
  rm -f "${read_only_profile}" "${read_only_overlay}"
else
  echo "[OK] read-only menu routes have no generated-file side effect"
fi

profile_id="validate_profile_$$"
profile_path="${REPO_ROOT}/test_log/runtime_configs/${profile_id}.profile.env"
profile_overlay="${REPO_ROOT}/test_log/runtime_configs/${profile_id}_overlay.yml"
invalid_profile="${REPO_ROOT}/test_log/runtime_configs/${profile_id}_invalid.profile.env"
rm -f "${profile_path}" "${profile_overlay}" "${invalid_profile}"
if printf '%s\n' "${profile_id}" "1,56" "106" "" "" "" "" "1" "1" \
  | bash "${MAIN_MENU}" experiment "${profile_path}" >/dev/null 2>&1; then
  echo "[OK] create versioned experiment profile"
else
  echo "[FAIL] create versioned experiment profile" >&2
  failures=$((failures + 1))
fi
check_file "${profile_path}" "versioned experiment profile"
check_command_failure "avoid experiment profile overwrite" bash "${MAIN_MENU}" experiment "${profile_path}"

if preview_output=$(bash "${MAIN_MENU}" preview-profile "${profile_path}" 2>/dev/null) \
  && [[ "${preview_output}" == *"REDCAP_EXPERIMENT_PROFILE_VERSION=1"* ]] \
  && [[ "${preview_output}" == *"MMTC_ACTIVE_UES=1,56"* ]] \
  && [[ "${preview_output}" == *"MMTC_START_XAPP=1"* ]] \
  && [[ "${preview_output}" == *"OAI_REDCAP_DAPP_GATE_D_MARKER=1"* ]]; then
  echo "[OK] validate and preview experiment profile"
else
  echo "[FAIL] validate and preview experiment profile" >&2
  failures=$((failures + 1))
fi

sed 's/REDCAP_CU_DU_SPLIT=0/REDCAP_CU_DU_SPLIT=1/' "${profile_path}" > "${invalid_profile}"
check_command_failure "reject CU/DU split profile" bash "${MAIN_MENU}" preview-profile "${invalid_profile}"
sed 's/REDCAP_GNB_COUNT=1/REDCAP_GNB_COUNT=2/' "${profile_path}" > "${invalid_profile}"
check_command_failure "reject multiple-gNB profile" bash "${MAIN_MENU}" preview-profile "${invalid_profile}"
sed 's/REDCAP_EXPERIMENT_PROFILE_VERSION=1/REDCAP_EXPERIMENT_PROFILE_VERSION=2/' "${profile_path}" > "${invalid_profile}"
check_command_failure "reject future profile version" bash "${MAIN_MENU}" preview-profile "${invalid_profile}"
sed 's/MMTC_ACTIVE_UES=1,56/MMTC_ACTIVE_UES=0/' "${profile_path}" > "${invalid_profile}"
check_command_failure "reject profile UE0" bash "${MAIN_MENU}" preview-profile "${invalid_profile}"
sed 's/MMTC_ACTIVE_UES=1,56/MMTC_ACTIVE_UES=57/' "${profile_path}" > "${invalid_profile}"
check_command_failure "reject profile UE57" bash "${MAIN_MENU}" preview-profile "${invalid_profile}"
sed 's/MMTC_ACTIVE_UES=1,56/MMTC_ACTIVE_UES=1,1/' "${profile_path}" > "${invalid_profile}"
check_command_failure "reject duplicate UE in profile" bash "${MAIN_MENU}" preview-profile "${invalid_profile}"
cp "${profile_path}" "${invalid_profile}"
printf 'MMTC_ACTIVE_UES=2\n' >> "${invalid_profile}"
check_command_failure "reject duplicate profile key" bash "${MAIN_MENU}" preview-profile "${invalid_profile}"
cp "${profile_path}" "${invalid_profile}"
printf 'UNSUPPORTED_PROFILE_KEY=1\n' >> "${invalid_profile}"
check_command_failure "reject unknown profile key" bash "${MAIN_MENU}" preview-profile "${invalid_profile}"

if run_output=$(MMTC_SMOKE_PREPARE_ONLY=1 bash "${MAIN_MENU}" run-profile "${profile_path}" smoke 2>&1) \
  && [[ "${run_output}" == *"Active UE selection : 1 56"* ]] \
  && [[ "${run_output}" == *"xapp-rc-moni"* ]] \
  && [[ "${run_output}" == *"Prepare-only mode active"* ]]; then
  echo "[OK] profile adapter reaches existing smoke path"
else
  echo "[FAIL] profile adapter did not reach expected smoke prepare-only path" >&2
  failures=$((failures + 1))
fi
check_command_failure "reject invalid profile run mode" bash "${MAIN_MENU}" run-profile "${profile_path}" unsupported
rm -f "${profile_path}" "${profile_overlay}" "${invalid_profile}"

invalid_overlay="/tmp/redcap_invalid_active_ues_$$.yml"
rm -f "${invalid_overlay}"
check_command_failure "reject empty MMTC_ACTIVE_UES" env MMTC_TOTAL_UES=56 MMTC_ACTIVE_UES= MMTC_OVERLAY_COMPOSE="${invalid_overlay}" bash "${LIB_DIR}/fc_mmtc_smoke_validation.sh"
check_command_failure "reject malformed MMTC_ACTIVE_UES" env MMTC_TOTAL_UES=56 MMTC_ACTIVE_UES=abc MMTC_OVERLAY_COMPOSE="${invalid_overlay}" bash "${LIB_DIR}/fc_mmtc_smoke_validation.sh"
check_command_failure "reject UE0" env MMTC_TOTAL_UES=56 MMTC_ACTIVE_UES=0 MMTC_OVERLAY_COMPOSE="${invalid_overlay}" bash "${LIB_DIR}/fc_mmtc_smoke_validation.sh"
check_command_failure "reject negative UE" env MMTC_TOTAL_UES=56 MMTC_ACTIVE_UES=-1 MMTC_OVERLAY_COMPOSE="${invalid_overlay}" bash "${LIB_DIR}/fc_mmtc_smoke_validation.sh"
check_command_failure "reject duplicate UE" env MMTC_TOTAL_UES=56 MMTC_ACTIVE_UES=1,1 MMTC_OVERLAY_COMPOSE="${invalid_overlay}" bash "${LIB_DIR}/fc_mmtc_smoke_validation.sh"
check_command_failure "reject UE57" env MMTC_TOTAL_UES=56 MMTC_ACTIVE_UES=57 MMTC_OVERLAY_COMPOSE="${invalid_overlay}" bash "${LIB_DIR}/fc_mmtc_smoke_validation.sh"
if [ -e "${invalid_overlay}" ]; then
  echo "[FAIL] invalid active UE input created a runtime overlay" >&2
  failures=$((failures + 1))
  rm -f "${invalid_overlay}"
else
  echo "[OK] invalid active UE input has no generated-file side effect"
fi

mkdir -p "${REPO_ROOT}/test_log/runtime_configs"
valid_overlay=$(mktemp "${REPO_ROOT}/test_log/runtime_configs/validate_active_ues.XXXXXX.yml")
check_command_success "accept UE1 and UE56" env MMTC_TOTAL_UES=56 MMTC_ACTIVE_UES="1, 56" MMTC_SMOKE_PREPARE_ONLY=1 MMTC_OVERLAY_COMPOSE="${valid_overlay}" bash "${LIB_DIR}/fc_mmtc_smoke_validation.sh"
check_file "${valid_overlay}" "validated UE1/UE56 prepare-only overlay"
rm -f "${valid_overlay}"

if [ "${failures}" -ne 0 ]; then
  echo "[FAIL] RedCap interface validation found ${failures} issue(s)" >&2
  exit 1
fi

echo "[PASS] RedCap interface validation completed"
