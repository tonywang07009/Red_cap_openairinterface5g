#!/usr/bin/env bash

set -euo pipefail

redcap_validate_run_mode()
{
  case "${1:-}" in
    --dry-run|--run)
      ;;
    *)
      echo "usage: $0 [--dry-run|--run]" >&2
      exit 2
      ;;
  esac
}

redcap_export_local_image_defaults()
{
  export REGISTRY="${REGISTRY:-${MMTC_IMAGE_REGISTRY:-}}"
  export TAG="${TAG:-${MMTC_IMAGE_TAG:-latest}}"
  export GNB_IMG="${GNB_IMG:-${MMTC_GNB_IMAGE_NAME:-oai-gnb}}"
  export NRUE_IMG="${NRUE_IMG:-${MMTC_NRUE_IMAGE_NAME:-oai-nr-ue}}"

  export MMTC_IMAGE_REGISTRY="${REGISTRY}"
  export MMTC_IMAGE_TAG="${TAG}"
  export MMTC_GNB_IMAGE_NAME="${GNB_IMG}"
  export MMTC_NRUE_IMAGE_NAME="${NRUE_IMG}"
}

redcap_export_rf_defaults()
{
  export MMTC_REDCAP_ENABLE="${MMTC_REDCAP_ENABLE:-1}"
  export MMTC_REDCAP_NUM_RX="${MMTC_REDCAP_NUM_RX:-1}"
  export MMTC_REDCAP_HALF_DUPLEX="${MMTC_REDCAP_HALF_DUPLEX:-1}"
  export MMTC_N_RB_DL="${MMTC_N_RB_DL:-106}"
  export MMTC_NUMEROLOGY="${MMTC_NUMEROLOGY:-1}"
  export MMTC_RF_FREQ="${MMTC_RF_FREQ:-3630360000}"
  export MMTC_SSB_START="${MMTC_SSB_START:-144}"
}

redcap_compose_up()
{
  local compose_dir="$1"
  shift

  (
    cd "${compose_dir}"
    local compose_args=(-f docker-compose.yml -f docker-compose.mmtc.yml up -d)
    if [[ "${REDCAP_COMPOSE_FORCE_RECREATE:-0}" == "1" ]]; then
      compose_args+=(--force-recreate)
    fi
    docker compose "${compose_args[@]}" "$@"
  )
}

redcap_compose_ps()
{
  local compose_dir="$1"

  (
    cd "${compose_dir}"
    docker compose -f docker-compose.yml -f docker-compose.mmtc.yml ps
  )
}

redcap_compose_stop()
{
  local compose_dir="$1"
  shift

  (
    cd "${compose_dir}"
    docker compose -f docker-compose.yml -f docker-compose.mmtc.yml stop "$@"
  )
}

redcap_collect_container_log()
{
  local label="$1"
  local container="$2"
  local container_log_dir="$3"
  local tail_lines="$4"
  local full_log_dir="${container_log_dir}/full"
  local full_log="${full_log_dir}/${label}.log"
  local tail_log="${container_log_dir}/${label}_tail.log"

  mkdir -p "${full_log_dir}"

  if docker inspect "${container}" >/dev/null 2>&1; then
    docker logs "${container}" > "${full_log}" 2>&1 || true
    tail -n "${tail_lines}" "${full_log}" > "${tail_log}" || true
  else
    echo "container not found: ${container}" > "${full_log}"
    cp "${full_log}" "${tail_log}"
  fi
}

redcap_collect_standard_runtime_logs()
{
  local log_dir="$1"
  local tail_lines="$2"
  local container_log_dir="${log_dir}/container_logs"

  redcap_collect_container_log "nearRT-RIC" "nearRT-RIC_redcap" "${container_log_dir}" "${tail_lines}"
  redcap_collect_container_log "gnb" "rfsim5g-oai-gnb_redcap" "${container_log_dir}" "${tail_lines}"
  redcap_collect_container_log "ue2" "rfsim5g-oai-nr-ue2_redcap" "${container_log_dir}" "${tail_lines}"
  redcap_collect_container_log "xapp_kpm_rc" "xapp-kpm-rc_redcap" "${container_log_dir}" "${tail_lines}"
}

redcap_extract_and_merge_runtime_metrics()
{
  local script_dir="$1"
  local project_dir="$2"
  local mode="$3"
  local log_dir="$4"
  local scenario="$5"
  local full_log_dir="${log_dir}/container_logs/full"
  local runtime_csv="${log_dir}/${mode}_runtime_metrics.csv"

  case "${mode}" in
    bwp)
      python3 "${script_dir}/extract_bwp_metrics.py" \
        --gnb-log "${full_log_dir}/gnb.log" \
        --ric-log "${full_log_dir}/nearRT-RIC.log" \
        --xapp-log "${full_log_dir}/xapp_kpm_rc.log" \
        --ue-log "${full_log_dir}/ue2.log" \
        --scenario "${scenario}" \
        --output "${runtime_csv}"
      python3 "${script_dir}/merge_runtime_metrics.py" \
        --target "${project_dir}/exp_result/BWP_results.csv" \
        --runtime "${runtime_csv}" \
        --replace-scenario
      ;;
    sdt)
      python3 "${script_dir}/extract_sdt_metrics.py" \
        --gnb-log "${full_log_dir}/gnb.log" \
        --ue-log "${full_log_dir}/ue2.log" \
        --scenario "${scenario}" \
        --output "${runtime_csv}"
      python3 "${script_dir}/merge_runtime_metrics.py" \
        --target "${project_dir}/exp_result/SDT_results.csv" \
        --runtime "${runtime_csv}" \
        --replace-scenario
      ;;
    *)
      echo "unsupported metric mode: ${mode}" >&2
      exit 2
      ;;
  esac

  echo "[${mode}] runtime csv: ${runtime_csv}"
}
