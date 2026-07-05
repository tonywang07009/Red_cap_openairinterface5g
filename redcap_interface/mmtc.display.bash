#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/..")
LIB_DIR="${SCRIPT_DIR}/bash_library"
EVALUATION_RECOVER_DIR="${REPO_ROOT}/redcap_doc/evluation_recover"
LOG_DIR="${REPO_ROOT}/test_log/compiler_logs"
AB_SDT_LOG_DIR="${REPO_ROOT}/test_log/ab_sdt_fast_access"

pause_for_enter()
{
  read -r -p "Press Enter to continue..."
}

show_latest_logs()
{
  local scan_dirs=()

  echo "[INFO] Latest RedCap runtime/display logs"
  [ -d "${LOG_DIR}" ] && scan_dirs+=("${LOG_DIR}")
  [ -d "${AB_SDT_LOG_DIR}" ] && scan_dirs+=("${AB_SDT_LOG_DIR}")
  if [ "${#scan_dirs[@]}" -eq 0 ]; then
    return 0
  fi

  find "${scan_dirs[@]}" -maxdepth 1 -type f \
    \( -name '*iperf*.log' -o -name '*mmtc_smoke*.log' -o -name '*panel*.log' -o -name '*_summary.md' -o -name '*_metrics.csv' -o -name '*_console.log' \) \
    -printf '%T@ %p\n' 2>/dev/null | sort -nr | awk 'NR <= 20 {sub(/^[^ ]+ /, ""); print}'
}

show_docs()
{
  echo "[INFO] Evaluation recovery manuals: ${EVALUATION_RECOVER_DIR}"
  find "${EVALUATION_RECOVER_DIR}" -maxdepth 1 -type f -name '*.md' -printf '%f\n' 2>/dev/null | sort
}

run_panel()
{
  python3 "${LIB_DIR}/fc_iperf_live_panel.py" "$@"
}

run_paper08()
{
  bash "${LIB_DIR}/fc_paper08_fig9_chanmod_batch.sh" "$@"
}

run_paper11_live()
{
  bash "${LIB_DIR}/fc_paper11_iperf_live_demo.sh" "$@"
}

run_paper11_table3()
{
  bash "${LIB_DIR}/fc_paper11_table3_peak_reproduction.sh" "$@"
}

run_sdt_ab()
{
  bash "${LIB_DIR}/fc_ab_sdt_fast_access_demo.sh" "$@"
}

run_legacy_paper07_menu()
{
  echo "[INFO] PAPER-07 bundle still lives in the legacy runtime menu."
  bash "${LIB_DIR}/fc_runtime_menu_legacy.sh"
}

dispatch_cli()
{
  case "${1:-}" in
    panel) shift; run_panel "$@" ;;
    paper08) shift; run_paper08 "$@" ;;
    paper11-live) shift; run_paper11_live "$@" ;;
    paper11-table3) shift; run_paper11_table3 "$@" ;;
    sdt-ab) shift; run_sdt_ab "$@" ;;
    paper07-menu) shift; run_legacy_paper07_menu "$@" ;;
    logs) show_latest_logs ;;
    docs) show_docs ;;
    "") return 1 ;;
    *)
      echo "[ERROR] Unknown display subcommand: $1" >&2
      echo "Known: panel, paper08, paper11-live, paper11-table3, sdt-ab, paper07-menu, logs, docs" >&2
      return 2
      ;;
  esac
}

main_menu()
{
  local choice
  while true; do
    cat <<EOF

RedCap mMTC Display Menu
Repo: ${REPO_ROOT}

1) PAPER-07 legacy reproduction menu
2) PAPER-08 Fig.9 channel model batch
3) PAPER-11 live iperf panel demo
4) PAPER-11 Table 3 peak-rate proxy
5) A/B SDT fast-access demo
6) Standalone iperf live panel
7) Show latest logs
8) Show evaluation manuals
q) Quit
EOF
    read -r -p "Choice: " choice
    case "${choice}" in
      1) run_legacy_paper07_menu; pause_for_enter ;;
      2) run_paper08; pause_for_enter ;;
      3) run_paper11_live; pause_for_enter ;;
      4) run_paper11_table3; pause_for_enter ;;
      5) run_sdt_ab; pause_for_enter ;;
      6) run_panel; pause_for_enter ;;
      7) show_latest_logs; pause_for_enter ;;
      8) show_docs; pause_for_enter ;;
      q|Q) exit 0 ;;
      *) echo "[WARN] Unknown choice: ${choice}" ;;
    esac
  done
}

if [ "$#" -gt 0 ]; then
  dispatch_cli "$@"
else
  main_menu
fi
