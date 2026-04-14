#!/usr/bin/env bash

set -euo pipefail

PREFIX=/opt/oai-nr-ue
LEGACY_TEMPLATE_CONFIGFILE="$PREFIX/etc/nr-ue.yaml"
DEFAULT_TEMPLATE_CONFIG_REDCAP="${MMTC_TEMPLATE_CONFIG_REDCAP:-$PREFIX/etc/nr-ue-redcap.yaml}"
DEFAULT_TEMPLATE_CONFIG_NORMAL="${MMTC_TEMPLATE_CONFIG_NORMAL:-$PREFIX/etc/nr-ue-normal.yaml}"
RUNTIME_CONFIGFILE="${MMTC_RUNTIME_CONFIG:-/tmp/nr-ue-mmtc.yaml}"

resolve_template_config()
{
  if [[ -n "${MMTC_TEMPLATE_CONFIG:-}" ]]; then
    printf '%s\n' "${MMTC_TEMPLATE_CONFIG}"
    return
  fi

  if [[ "${MMTC_REDCAP_ENABLE:-1}" == "0" ]]; then
    printf '%s\n' "${DEFAULT_TEMPLATE_CONFIG_NORMAL}"
    return
  fi

  printf '%s\n' "${DEFAULT_TEMPLATE_CONFIG_REDCAP}"
}

TEMPLATE_CONFIGFILE="$(resolve_template_config)"

echo "=================================="
echo "/proc/sys/kernel/core_pattern=$(cat /proc/sys/kernel/core_pattern)"

if [[ ! -f "$TEMPLATE_CONFIGFILE" ]]; then
  if [[ -f "$LEGACY_TEMPLATE_CONFIGFILE" ]]; then
    echo "Template configuration file $TEMPLATE_CONFIGFILE not found, falling back to $LEGACY_TEMPLATE_CONFIGFILE"
    TEMPLATE_CONFIGFILE="$LEGACY_TEMPLATE_CONFIGFILE"
  else
    echo "No template configuration file $TEMPLATE_CONFIGFILE found"
    exit 255
  fi
fi

if [[ -z "${MMTC_IMSI:-}" && -n "${MMTC_UE_INDEX:-}" ]]; then
  MMTC_IMSI=$(printf '001010%09d' "${MMTC_UE_INDEX}")
fi

cp "$TEMPLATE_CONFIGFILE" "$RUNTIME_CONFIGFILE"

update_yaml_scalar()
{
  local key="$1"
  local value="$2"
  sed -i -E "s/^([[:space:]]*${key}:).*/\\1 ${value}/" "$RUNTIME_CONFIGFILE"
}

if [[ -n "${MMTC_IMSI:-}" ]]; then
  update_yaml_scalar "imsi" "$MMTC_IMSI"
fi

if grep -q '^nrue_recap:' "$RUNTIME_CONFIGFILE"; then
  [[ -n "${MMTC_REDCAP_ENABLE:-}" ]] && update_yaml_scalar "enable" "$MMTC_REDCAP_ENABLE"
  [[ -n "${MMTC_REDCAP_ENABLE:-}" ]] && update_yaml_scalar "support_of_redcap_r17" "$MMTC_REDCAP_ENABLE"
  [[ -n "${MMTC_REDCAP_NUM_RX:-}" ]] && update_yaml_scalar "number_of_rx_redcap_r17" "$MMTC_REDCAP_NUM_RX"
  [[ -n "${MMTC_REDCAP_HALF_DUPLEX:-}" ]] && update_yaml_scalar "half_duplex_fdd_type_a_redcap_r17" "$MMTC_REDCAP_HALF_DUPLEX"
fi

[[ -n "${MMTC_BAND:-}" ]] && update_yaml_scalar "band" "$MMTC_BAND"
[[ -n "${MMTC_RF_FREQ:-}" ]] && update_yaml_scalar "rf_freq" "$MMTC_RF_FREQ"
[[ -n "${MMTC_NUMEROLOGY:-}" ]] && update_yaml_scalar "numerology" "$MMTC_NUMEROLOGY"
[[ -n "${MMTC_N_RB_DL:-}" ]] && update_yaml_scalar "N_RB_DL" "$MMTC_N_RB_DL"
[[ -n "${MMTC_SSB_START:-}" ]] && update_yaml_scalar "ssb_start" "$MMTC_SSB_START"

echo "=================================="
echo "== Generated mMTC configuration file:"
cat "$RUNTIME_CONFIGFILE"

new_args=()
while [[ $# -gt 0 ]]; do
  new_args+=("$1")
  shift
done

new_args+=("-O")
new_args+=("$RUNTIME_CONFIGFILE")

export OAI_GDBSTACKS=1

echo "=================================="
echo "== Starting NR UE soft modem (mMTC overlay)"
if [[ -v USE_ADDITIONAL_OPTIONS ]]; then
  echo "Additional option(s): ${USE_ADDITIONAL_OPTIONS}"
  for word in ${USE_ADDITIONAL_OPTIONS}; do
    new_args+=("$word")
  done
fi

echo "${new_args[@]}"
exec "${new_args[@]}"
