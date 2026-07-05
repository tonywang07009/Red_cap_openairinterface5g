#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
exec "${SCRIPT_DIR}/bash_library/fc_runtime_e2_ab_test.sh" "$@"
