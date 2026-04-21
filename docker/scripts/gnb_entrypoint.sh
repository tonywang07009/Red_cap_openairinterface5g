#!/bin/bash

set -uo pipefail

PREFIX=/opt/oai-gnb
CONFIGFILE=$PREFIX/etc/gnb.conf
MMTC_SEGV_BT="${MMTC_SEGV_BACKTRACE:-0}"
MMTC_SIG_DIAG=0

if [[ "$MMTC_SEGV_BT" =~ ^[0-9]+$ ]] && [ "$MMTC_SEGV_BT" -gt 0 ]; then
  MMTC_SIG_DIAG=1
fi

mmtc_forward_signal()
{
  local sig="$1"
  local child_pid="$2"
  echo "[CGDBG][ENTRYPOINT] caught signal ${sig} pid=$$ child_pid=${child_pid:-none}"
  if [ -n "$child_pid" ] && kill -0 "$child_pid" 2>/dev/null; then
    kill "-$sig" "$child_pid" 2>/dev/null || true
  fi
}

echo "=================================="
echo "/proc/sys/kernel/core_pattern=$(cat /proc/sys/kernel/core_pattern)"

if [ ! -f $CONFIGFILE ]; then
  echo "No configuration file $CONFIGFILE found: attempting to find YAML config"
  YAML_CONFIGFILE=$PREFIX/etc/gnb.yaml
  if [ ! -f $YAML_CONFIGFILE ]; then
    echo "No configuration file $YAML_CONFIGFILE found. Please mount either at $CONFIGFILE or $YAML_CONFIGFILE"
    exit 255
  fi
  CONFIGFILE=$YAML_CONFIGFILE
fi

echo "=================================="
echo "== Configuration file:"
cat $CONFIGFILE

new_args=()

while [[ $# -gt 0 ]]; do
  new_args+=("$1")
  shift
done

new_args+=("-O")
new_args+=("$CONFIGFILE")

# Load the USRP binaries
echo "=================================="
echo "== Load USRP binaries"
if [[ -v USE_B2XX ]]; then
    $PREFIX/bin/uhd_images_downloader.py -t b2xx
elif [[ -v USE_X3XX ]]; then
    $PREFIX/bin/uhd_images_downloader.py -t x3xx
elif [[ -v USE_N3XX ]]; then
    $PREFIX/bin/uhd_images_downloader.py -t n3xx
fi

# enable printing of stack traces on assert
export OAI_GDBSTACKS=1

echo "=================================="
echo "== Starting gNB soft modem"
echo "[CGDBG][ENTRYPOINT] MMTC_SEGV_BACKTRACE=${MMTC_SEGV_BT} diag_mode=${MMTC_SIG_DIAG} pid=$$"
if [[ -v USE_ADDITIONAL_OPTIONS ]]; then
    echo "Additional option(s): ${USE_ADDITIONAL_OPTIONS}"
    while [[ $# -gt 0 ]]; do
        new_args+=("$1")
        shift
    done
    for word in ${USE_ADDITIONAL_OPTIONS}; do
        new_args+=("$word")
    done
    echo "${new_args[@]}"
else
    echo "${new_args[@]}"
fi

if [ "$MMTC_SIG_DIAG" -gt 0 ]; then
  CHILD_PID=""
  trap 'mmtc_forward_signal TERM "$CHILD_PID"' TERM
  trap 'mmtc_forward_signal INT "$CHILD_PID"' INT
  trap 'mmtc_forward_signal QUIT "$CHILD_PID"' QUIT
  trap 'mmtc_forward_signal HUP "$CHILD_PID"' HUP

  "${new_args[@]}" &
  CHILD_PID=$!
  echo "[CGDBG][ENTRYPOINT] launched child pid=${CHILD_PID}"
  wait "$CHILD_PID"
  child_rc=$?
  echo "[CGDBG][ENTRYPOINT] child exit rc=${child_rc}"
  exit "$child_rc"
fi

exec "${new_args[@]}"
