#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/../..")
CN_COMPOSE="${REPO_ROOT}/oai-cn5g/docker-compose.yaml"
RAN_COMPOSE="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml"
SMOKE_RUNNER="${SCRIPT_DIR}/fc_mmtc_smoke_validation.sh"
LOCAL_RAN_BUILDER="${SCRIPT_DIR}/fc_rebuild_local_oai_images.sh"
BUILD_OAI="${REPO_ROOT}/cmake_targets/build_oai"
TASK_MANIFEST="${REPO_ROOT}/task_log/tasks.json"
MIN_FREE_GB=${REDCAP_INSTALL_MIN_FREE_GB:-40}
if ! [[ "${MIN_FREE_GB}" =~ ^[0-9]+$ ]] || (( MIN_FREE_GB < 40 )); then
  echo "[ERROR] REDCAP_INSTALL_MIN_FREE_GB must be an integer of at least 40." >&2
  exit 2
fi
TIMESTAMP=$(date +%F_%H-%M-%S)
LOG_DIR="${REPO_ROOT}/test_log/compiler_logs"
RUNTIME_CONFIG_DIR="${REPO_ROOT}/test_log/runtime_configs"
INSTALL_LOG="${LOG_DIR}/redcap_install_${TIMESTAMP}.log"
SMOKE_LOG="${LOG_DIR}/redcap_install_${TIMESTAMP}_1ue_smoke.log"
SMOKE_OVERLAY="${RUNTIME_CONFIG_DIR}/redcap_install_${TIMESTAMP}_overlay.yml"
TASK_ID="redcap-interactive-install-${TIMESTAMP}"
INSTALL_LOCK="/tmp/redcap-interactive-install.lock"
TASK_RUNNING=0
SMOKE_OWNED=0

show_help()
{
  cat <<'EOF'
RedCap 互動安裝器

用法：
  ./mmtc.menu.bash install
  ./mmtc.menu.bash install --check
  ./mmtc.menu.bash install --help

模式：
  install          互動確認 uv、OAI 依賴、Docker image、本機 RedCap/FlexRIC build 與預設 1 UE smoke。
  install --check  唯讀檢查 host、Compose、uv lock 與本機 image；不下載、不 build、不啟動 Docker。

支援基線：Ubuntu 22.04、Python >=3.12、Docker Compose v2 語法、至少 40 GiB 可用空間。
可用 REDCAP_INSTALL_MIN_FREE_GB 覆寫最低空間門檻。

RedCap interactive installer

Usage:
  ./mmtc.menu.bash install
  ./mmtc.menu.bash install --check
  ./mmtc.menu.bash install --help

Modes:
  install          Confirm uv, OAI dependencies, Docker images, local RedCap/FlexRIC builds, and the default 1 UE smoke.
  install --check  Read-only host, Compose, uv lock, and local-image checks; no downloads, builds, or containers.

Supported baseline: Ubuntu 22.04, Python >=3.12, Docker Compose v2 syntax, and at least 40 GiB free space.
Set REDCAP_INSTALL_MIN_FREE_GB to raise the free-space threshold.
EOF
}

confirm()
{
  local prompt="$1"
  local default=${2:-n}
  local answer
  local suffix="[y/N]"
  [ "${default}" = "y" ] && suffix="[Y/n]"
  read -r -p "${prompt} ${suffix} " answer
  answer=${answer:-${default}}
  [[ "${answer,,}" = "y" || "${answer,,}" = "yes" ]]
}

compose_metadata()
{
  local compose_file="$1"
  local field="$2"
  docker compose -f "${compose_file}" config --format json | python3 -c '
import json, sys
data = json.load(sys.stdin)
services = data.get("services", {})
build_images = {v.get("image") for v in services.values() if v.get("build") and v.get("image")}
field = sys.argv[1]
if field == "remote-images":
    values = {v.get("image") for v in services.values() if v.get("image") and v.get("image") not in build_images}
elif field == "build-images":
    values = build_images
elif field == "build-services":
    values = {k for k, v in services.items() if v.get("build")}
else:
    raise SystemExit(f"unsupported metadata field: {field}")
print("\n".join(sorted(values)))
' "${field}"
}

remote_images()
{
  {
    compose_metadata "${CN_COMPOSE}" remote-images
    compose_metadata "${RAN_COMPOSE}" remote-images
  } | sort -u
}

build_images()
{
  compose_metadata "${RAN_COMPOSE}" build-images
}

build_services()
{
  compose_metadata "${RAN_COMPOSE}" build-services
}

ran_image_contract()
{
  local mode=${1:-compose}
  local compose_command=(docker compose -f "${RAN_COMPOSE}" config --format json)
  if [ "${mode}" = "local" ]; then
    compose_command=(env REGISTRY= TAG=latest docker compose -f "${RAN_COMPOSE}" config --format json)
  elif [ "${mode}" != "compose" ]; then
    echo "unsupported RAN image-contract mode: ${mode}" >&2
    return 2
  fi
  "${compose_command[@]}" | python3 -c '
import json, sys

services = json.load(sys.stdin)["services"]
references = [services["oai-gnb"]["image"], services["oai-nr-ue1"]["image"]]
parts = []
for reference in references:
    path, separator, tag = reference.rpartition(":")
    if not separator or "@" in reference:
        raise SystemExit(f"unsupported RAN image reference: {reference}")
    registry, slash, name = path.rpartition("/")
    parts.append(((registry + "/") if slash else "", name, tag))
if parts[0][0] != parts[1][0] or parts[0][2] != parts[1][2]:
    raise SystemExit("gNB and NR UE images require different registry/tag contracts")
print(parts[0][0] or "-", parts[0][2], parts[0][1], parts[1][1])
'
}

local_ran_images()
{
  local registry tag gnb_name nrue_name
  read -r registry tag gnb_name nrue_name < <(ran_image_contract local)
  [ "${registry}" = "-" ] && registry=""
  printf '%s\n' "${registry}${gnb_name}:${tag}" "${registry}${nrue_name}:${tag}"
}

update_task()
{
  local status="$1"
  local next_action="$2"
  mkdir -p "$(dirname "${TASK_MANIFEST}")"
  python3 - "${TASK_MANIFEST}" "${TASK_ID}" "${status}" "${next_action}" \
    "${INSTALL_LOG#${REPO_ROOT}/}" <<'PY'
import json
import os
import sys
from datetime import datetime
from pathlib import Path

path = Path(sys.argv[1])
task_id, status, next_action, log_path = sys.argv[2:]
now = datetime.now().astimezone().isoformat(timespec="seconds")
data = json.loads(path.read_text()) if path.exists() else {"version": 1, "tasks": []}
task = next((item for item in data["tasks"] if item.get("task_id") == task_id), None)
if task is None:
    task = {"task_id": task_id}
    data["tasks"].append(task)
task.update({
    "status": status,
    "command": "./mmtc.menu.bash install",
    "log_path": log_path,
    "side_effects": "Synchronizes uv, pulls declared images, builds local RedCap and declared Compose services, and runs a clean 1 UE smoke.",
    "next_action": next_action,
})
if status == "running":
    task["started_at"] = now
    task["completed_at"] = None
elif status in {"passed", "failed", "blocked"}:
    task.setdefault("started_at", now)
    task["completed_at"] = now
tmp = path.with_suffix(path.suffix + ".tmp")
tmp.write_text(json.dumps(data, indent=2) + "\n")
os.replace(tmp, path)
PY
}

check_python_version()
{
  python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 12))'
}

check_host()
{
  local mode="$1"
  local failures=0
  local version_id=""
  local free_gb=0
  local command

  [ -r /etc/os-release ] && version_id=$(sed -n 's/^VERSION_ID="\?\([^" ]*\)"\?$/\1/p' /etc/os-release)
  if [ "${version_id}" = "22.04" ]; then
    echo "[OK] Ubuntu ${version_id}"
  else
    echo "[BLOCKED] Supported host baseline is Ubuntu 22.04; detected '${version_id:-unknown}'." >&2
    failures=$((failures + 1))
  fi

  for command in realpath python3 docker df sort awk rg flock; do
    if command -v "${command}" >/dev/null 2>&1; then
      echo "[OK] command: ${command}"
    else
      echo "[BLOCKED] missing command: ${command}" >&2
      failures=$((failures + 1))
    fi
  done

  for required_path in "${CN_COMPOSE}" "${RAN_COMPOSE}" "${SMOKE_RUNNER}" "${LOCAL_RAN_BUILDER}" "${REPO_ROOT}/pyproject.toml"; do
    if [ -f "${required_path}" ]; then
      echo "[OK] repository path: ${required_path#${REPO_ROOT}/}"
    else
      echo "[BLOCKED] repository path is missing: ${required_path#${REPO_ROOT}/}" >&2
      failures=$((failures + 1))
    fi
  done

  if check_python_version; then
    echo "[OK] $(python3 --version)"
  else
    echo "[BLOCKED] Python 3.12 or newer is required." >&2
    failures=$((failures + 1))
  fi

  free_gb=$(df -Pk "${REPO_ROOT}" | awk 'NR==2 {print int($4 / 1024 / 1024)}')
  if (( free_gb >= MIN_FREE_GB )); then
    echo "[OK] free disk: ${free_gb} GiB (minimum ${MIN_FREE_GB} GiB)"
  else
    echo "[BLOCKED] free disk ${free_gb} GiB is below ${MIN_FREE_GB} GiB." >&2
    failures=$((failures + 1))
  fi

  if docker compose version >/dev/null 2>&1; then
    echo "[OK] $(docker compose version)"
  else
    echo "[BLOCKED] Docker Compose v2 syntax is unavailable." >&2
    failures=$((failures + 1))
  fi
  if docker info >/dev/null 2>&1; then
    echo "[OK] Docker API access"
  else
    echo "[BLOCKED] Docker API is unavailable; check the daemon and group membership." >&2
    failures=$((failures + 1))
  fi

  for compose_file in "${CN_COMPOSE}" "${RAN_COMPOSE}"; do
    if docker compose -f "${compose_file}" config --quiet; then
      echo "[OK] Compose: ${compose_file#${REPO_ROOT}/}"
    else
      echo "[BLOCKED] Invalid Compose: ${compose_file#${REPO_ROOT}/}" >&2
      failures=$((failures + 1))
    fi
  done

  if command -v uv >/dev/null 2>&1; then
    echo "[OK] $(uv --version)"
    if { [ "${mode}" = "check" ] && uv lock --check --offline >/dev/null 2>&1; } \
      || { [ "${mode}" != "check" ] && uv lock --check >/dev/null 2>&1; }; then
      echo "[OK] uv.lock matches pyproject.toml"
    else
      echo "[BLOCKED] uv.lock is missing or stale; run and review 'uv lock'." >&2
      failures=$((failures + 1))
    fi
  elif [ "${mode}" = "check" ]; then
    echo "[BLOCKED] uv is not installed." >&2
    failures=$((failures + 1))
  else
    echo "[WARN] uv is not installed; interactive bootstrap is available."
  fi

  if [ "${mode}" = "check" ] && docker info >/dev/null 2>&1; then
    while IFS= read -r image; do
      [ -n "${image}" ] || continue
      if docker image inspect "${image}" >/dev/null 2>&1; then
        echo "[OK] remote image present: ${image}"
      else
        echo "[BLOCKED] remote image missing: ${image}" >&2
        failures=$((failures + 1))
      fi
    done < <(remote_images)
    while IFS= read -r image; do
      [ -n "${image}" ] || continue
      if docker image inspect "${image}" >/dev/null 2>&1; then
        echo "[OK] local build image present: ${image}"
      else
        echo "[BLOCKED] local build image missing: ${image}" >&2
        failures=$((failures + 1))
      fi
    done < <(build_images)
    while IFS= read -r image; do
      [ -n "${image}" ] || continue
      if docker image inspect "${image}" >/dev/null 2>&1; then
        echo "[OK] local RedCap runtime image present: ${image}"
      else
        echo "[BLOCKED] local RedCap runtime image missing: ${image}" >&2
        failures=$((failures + 1))
      fi
    done < <(local_ran_images)
  fi

  [ "${failures}" -eq 0 ]
}

bootstrap_uv()
{
  local installer
  command -v curl >/dev/null 2>&1 || { echo "[BLOCKED] curl is required for uv bootstrap." >&2; return 1; }
  installer=$(mktemp /tmp/redcap-uv-install.XXXXXX.sh)
  curl -LsSf https://astral.sh/uv/install.sh -o "${installer}"
  sh "${installer}"
  rm -f "${installer}"
  if [ -n "${HOME:-}" ]; then
    export PATH="${HOME}/.local/bin:${PATH}"
  fi
  command -v uv >/dev/null 2>&1
}

missing_oai_build_commands()
{
  local command
  for command in cmake ninja gcc g++; do
    command -v "${command}" >/dev/null 2>&1 || printf '%s\n' "${command}"
  done
}

pull_declared_images()
{
  local image
  while IFS= read -r image; do
    [ -n "${image}" ] || continue
    echo "[COMMAND $(date --iso-8601=seconds)] docker pull ${image}"
    docker pull "${image}"
  done < <(remote_images)
}

build_declared_services()
{
  local services=()
  mapfile -t services < <(build_services)
  [ "${#services[@]}" -gt 0 ] || return 0
  echo "[COMMAND $(date --iso-8601=seconds)] docker compose -f ${RAN_COMPOSE#${REPO_ROOT}/} build --pull ${services[*]}"
  docker compose -f "${RAN_COMPOSE}" build --pull "${services[@]}"
}

local_ran_images_present()
{
  local image
  while IFS= read -r image; do
    [ -n "${image}" ] || continue
    docker image inspect "${image}" >/dev/null 2>&1 || return 1
  done < <(local_ran_images)
}

build_local_ran_images()
{
  echo "[COMMAND $(date --iso-8601=seconds)] bash ${LOCAL_RAN_BUILDER#${REPO_ROOT}/}"
  bash "${LOCAL_RAN_BUILDER}"
}

verify_declared_images()
{
  local image
  local failures=0
  while IFS= read -r image; do
    [ -n "${image}" ] || continue
    if ! docker image inspect "${image}" >/dev/null 2>&1; then
      echo "[BLOCKED] required remote image is absent: ${image}" >&2
      failures=$((failures + 1))
    fi
  done < <(remote_images)
  while IFS= read -r image; do
    [ -n "${image}" ] || continue
    if ! docker image inspect "${image}" >/dev/null 2>&1; then
      echo "[BLOCKED] required local build image is absent: ${image}" >&2
      failures=$((failures + 1))
    fi
  done < <(build_images)
  while IFS= read -r image; do
    [ -n "${image}" ] || continue
    if ! docker image inspect "${image}" >/dev/null 2>&1; then
      echo "[BLOCKED] required local RedCap runtime image is absent: ${image}" >&2
      failures=$((failures + 1))
    fi
  done < <(local_ran_images)
  [ "${failures}" -eq 0 ]
}

managed_containers_exist()
{
  [ -n "$(docker compose -f "${CN_COMPOSE}" ps -a -q 2>/dev/null)" ] || \
    [ -n "$(docker compose -f "${RAN_COMPOSE}" ps -a -q 2>/dev/null)" ]
}

cleanup_smoke()
{
  [ "${SMOKE_OWNED}" -eq 1 ] || return 0
  echo "[CLEANUP] Stop installer-owned RFsim and CN5G services"
  docker compose --env-file /dev/null -f "${RAN_COMPOSE}" -f "${SMOKE_OVERLAY}" down --remove-orphans || true
  docker compose --env-file /dev/null -f "${CN_COMPOSE}" down --remove-orphans || true
  SMOKE_OWNED=0
}

on_exit()
{
  local rc=$?
  cleanup_smoke
  if [ "${TASK_RUNNING}" -eq 1 ]; then
    update_task failed "inspect_log"
  fi
  return "${rc}"
}

run_one_ue_smoke()
{
  local smoke_registry smoke_tag smoke_gnb_name smoke_nrue_name
  if managed_containers_exist; then
    echo "[BLOCKED] Managed CN5G or RFsim containers already exist; stop them explicitly before installer smoke." >&2
    return 1
  fi
  read -r smoke_registry smoke_tag smoke_gnb_name smoke_nrue_name < <(ran_image_contract local)
  [ "${smoke_registry}" = "-" ] && smoke_registry=""
  SMOKE_OWNED=1
  echo "[COMMAND $(date --iso-8601=seconds)] MMTC_TOTAL_UES=56 MMTC_ACTIVE_UES=1 MMTC_IMAGE_REGISTRY=${smoke_registry} MMTC_IMAGE_TAG=${smoke_tag} bash ${SMOKE_RUNNER#${REPO_ROOT}/}"
  set +e
  MMTC_TOTAL_UES=56 \
  MMTC_ACTIVE_UES=1 \
  MMTC_IMAGE_REGISTRY="${smoke_registry}" \
  MMTC_IMAGE_TAG="${smoke_tag}" \
  MMTC_GNB_IMAGE_NAME="${smoke_gnb_name}" \
  MMTC_NRUE_IMAGE_NAME="${smoke_nrue_name}" \
  MMTC_START_XAPP=0 \
  MMTC_USE_EXISTING_CN_DB=0 \
  MMTC_RUN_REVERSE_PING=0 \
  MMTC_IPERF_ENABLE=0 \
  MMTC_OVERLAY_COMPOSE="${SMOKE_OVERLAY}" \
    bash "${SMOKE_RUNNER}" 2>&1 | tee "${SMOKE_LOG}"
  local smoke_rc=${PIPESTATUS[0]}
  set -e
  if [ "${smoke_rc}" -ne 0 ]; then
    echo "[FAILED] 1 UE smoke command failed; log: ${SMOKE_LOG#${REPO_ROOT}/}" >&2
    return 1
  fi
  if ! smoke_summary_passes "${SMOKE_LOG}"; then
    echo "[FAILED] 1 UE smoke summary markers are incomplete; log: ${SMOKE_LOG#${REPO_ROOT}/}" >&2
    return 1
  fi
  echo "[PASS] 1 UE smoke: attach=1 pdu=1 tun=1 forward_ping_ok=1 gnb_restart=0 failures=0"
  cleanup_smoke
}

smoke_summary_passes()
{
  local log_path="$1"
  rg -q '^\[SUMMARY\] sample=1 active=1 running=1 attach=1 pdu=1 tun=1 forward_ping_ok=1 .*gnb_restart=0 failures=0 ' "${log_path}"
}

run_interactive()
{
  local missing_commands=()
  cat <<'EOF'
Install stages / 安裝階段：
  1. Read-only host and Compose preflight
  2. uv bootstrap when missing and uv sync --locked
  3. Existing upstream OAI dependency installer when build commands are missing
  4. Pull Compose-declared remote images
  5. Build or reuse project-local RedCap gNB/NR UE images
  6. Build Compose-declared local FlexRIC service
  7. Default clean 1 UE smoke and cleanup
EOF
  confirm "Continue with the interactive installation? / 繼續互動安裝？" n || return 0
  exec 9>"${INSTALL_LOCK}"
  if ! flock -n 9; then
    echo "[BLOCKED] another interactive RedCap installer is running." >&2
    return 1
  fi
  mkdir -p "${LOG_DIR}" "${RUNTIME_CONFIG_DIR}"
  exec > >(tee -a "${INSTALL_LOG}") 2>&1
  trap on_exit EXIT

  check_host interactive || return 1
  if ! command -v uv >/dev/null 2>&1; then
    confirm "Install uv with the official standalone installer? / 使用官方安裝器安裝 uv？" n || {
      echo "[BLOCKED] uv bootstrap declined."
      return 1
    }
    bootstrap_uv
  fi
  uv lock --check

  update_task running "complete_install"
  TASK_RUNNING=1

  confirm "Synchronize Python with uv sync --locked? / 同步 Python 環境？" y && uv sync --locked

  mapfile -t missing_commands < <(missing_oai_build_commands)
  if [ "${#missing_commands[@]}" -gt 0 ]; then
    echo "[WARN] Missing OAI build commands: ${missing_commands[*]}"
    confirm "Run the upstream OAI dependency installer? / 執行上游 OAI 依賴安裝？" y || return 1
    (cd "${REPO_ROOT}/cmake_targets" && "${BUILD_OAI}" -I --install-optional-packages -w USRP)
  fi

  if confirm "Pull Compose-declared remote images? / 拉取 Compose 宣告的遠端 images？" y; then
    pull_declared_images
  else
    echo "[INFO] Remote image pull skipped by user."
  fi
  if local_ran_images_present; then
    if confirm "Rebuild existing local RedCap gNB/NR UE images? / 重建既有本機 RedCap gNB/NR UE images？" n; then
      build_local_ran_images
    else
      echo "[INFO] Reuse existing project-local RedCap runtime images."
    fi
  else
    confirm "Build required local RedCap gNB/NR UE images? / 建置必要的本機 RedCap gNB/NR UE images？" y || return 1
    build_local_ran_images
  fi
  if confirm "Build the Compose-declared local FlexRIC image? / 建置 Compose 宣告的本機 FlexRIC image？" y; then
    build_declared_services
  else
    echo "[INFO] Local FlexRIC build skipped by user."
  fi
  verify_declared_images || return 1

  if confirm "Run the default clean 1 UE smoke now? / 現在執行預設 1 UE smoke？" y; then
    run_one_ue_smoke
  else
    echo "[BLOCKED] Installation assets were prepared, but the required 1 UE acceptance was not run."
    update_task blocked "run_1ue_smoke"
    TASK_RUNNING=0
    trap - EXIT
    return 1
  fi

  update_task passed "update_documentation"
  TASK_RUNNING=0
  trap - EXIT
  echo "[PASS] RedCap installation accepted; log: ${INSTALL_LOG#${REPO_ROOT}/}"
  echo "[INFO] This does not prove the separate 29 UE newcomer gate."
}

main()
{
  case "${1:-}" in
    "") run_interactive ;;
    -h|--help) show_help ;;
    --check) check_host check ;;
    *)
      echo "[ERROR] unsupported installer option: $1" >&2
      show_help >&2
      return 2
      ;;
  esac
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  main "$@"
fi
