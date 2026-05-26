#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
exec "${SCRIPT_DIR}/redcap_runtime_menu.sh" "$@"
