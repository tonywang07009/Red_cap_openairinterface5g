#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/..")
TIMESTAMP=$(date +%F_%H-%M-%S)

TOTAL_UES=${MMTC_TOTAL_UES:-64}
SAMPLE_UES_RAW=${MMTC_SAMPLE_UES:-"29 32 64"}
EXT_DN_IP=${MMTC_EXT_DN_IP:-}
LEGACY_EXT_DN_IP=${MMTC_LEGACY_EXT_DN_IP:-12.1.1.1}
PING_COUNT=${MMTC_PING_COUNT:-10}
REVERSE_PING_COUNT=${MMTC_REVERSE_PING_COUNT:-3}
SLEEP_AFTER_UP=${MMTC_SLEEP_AFTER_UP:-25}
START_XAPP=${MMTC_START_XAPP:-0}
PREPARE_ONLY=${MMTC_SMOKE_PREPARE_ONLY:-0}
RESET_CN=${MMTC_RESET_CN:-1}

OVERLAY_GENERATOR="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh"
CN_DB_GENERATOR="${REPO_ROOT}/ci-scripts/generate_mmtc_cn_db_overlay.sh"
BASE_COMPOSE="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml"
OVERLAY_COMPOSE="${REPO_ROOT}/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml"
CN_COMPOSE="${REPO_ROOT}/doc/tutorial_resources/oai-cn5g/docker-compose.yaml"
LOG_DIR="${REPO_ROOT}/test_log/compiler_logs"
RUNTIME_CONFIG_DIR="${REPO_ROOT}/test_log/runtime_configs"
FAILURES=0

mkdir -p "${LOG_DIR}"
mkdir -p "${RUNTIME_CONFIG_DIR}"

capture_cmd()
{
  local output_file="$1"
  shift
  {
    echo "# collected_at=$(date --iso-8601=seconds)"
    echo "# command: $*"
    "$@" 2>&1
  } > "${output_file}" || true
}

capture_container_snapshot()
{
  local label="$1"
  local container_name="$2"
  local output_file="$3"

  {
    echo "# label=${label}"
    echo "# container=${container_name}"
    echo "# collected_at=$(date --iso-8601=seconds)"
    docker inspect "${container_name}" --format '{{json .State}}' 2>&1 || true
    docker exec "${container_name}" sh -c '
      echo "## ip -br address"
      ip -br address || true
      echo
      echo "## ip route"
      ip route || true
      echo
      echo "## ip rule"
      ip rule show || true
      echo
      echo "## ss -u -a -n"
      ss -u -a -n || true
      echo
      echo "## /proc/net/dev"
      cat /proc/net/dev || true
    ' 2>&1 || true
  } > "${output_file}" || true
}

extract_tun_ipv4()
{
  local tun_log="$1"
  awk '/inet / {print $2; exit}' "${tun_log}" | cut -d/ -f1
}

derive_subnet_peer_ipv4()
{
  local ue_ipv4="$1"
  local o1 o2 o3 o4

  if [ -z "${ue_ipv4}" ]; then
    return 0
  fi

  IFS=. read -r o1 o2 o3 o4 <<EOF
${ue_ipv4}
EOF

  if [ -z "${o1:-}" ] || [ -z "${o2:-}" ] || [ -z "${o3:-}" ] || [ -z "${o4:-}" ]; then
    return 0
  fi

  if [ "${o4}" = "1" ]; then
    printf '%s.%s.%s.2\n' "${o1}" "${o2}" "${o3}"
    return 0
  fi

  printf '%s.%s.%s.1\n' "${o1}" "${o2}" "${o3}"
}

same_slash24_subnet()
{
  local lhs="$1"
  local rhs="$2"
  local l1 l2 l3 l4 r1 r2 r3 r4

  IFS=. read -r l1 l2 l3 l4 <<EOF
${lhs}
EOF
  IFS=. read -r r1 r2 r3 r4 <<EOF
${rhs}
EOF

  [ -n "${l1:-}" ] && [ -n "${l2:-}" ] && [ -n "${l3:-}" ] && \
  [ -n "${r1:-}" ] && [ -n "${r2:-}" ] && [ -n "${r3:-}" ] && \
  [ "${l1}.${l2}.${l3}" = "${r1}.${r2}.${r3}" ]
}

mapfile -t SAMPLE_UES < <(printf '%s\n' "${SAMPLE_UES_RAW}" | tr ', ' '\n' | sed '/^$/d')

if [ "${#SAMPLE_UES[@]}" -eq 0 ]; then
  echo "No sample UEs specified via MMTC_SAMPLE_UES" >&2
  exit 1
fi

for ue_idx in "${SAMPLE_UES[@]}"; do
  if ! [[ "${ue_idx}" =~ ^[0-9]+$ ]]; then
    echo "Invalid UE index in MMTC_SAMPLE_UES: ${ue_idx}" >&2
    exit 1
  fi
done

"${OVERLAY_GENERATOR}" "${TOTAL_UES}" "${OVERLAY_COMPOSE}"

CN_DB_SQL="${RUNTIME_CONFIG_DIR}/oai_db_mmtc_${TOTAL_UES}.sql"
CN_DB_COMPOSE_OVERLAY="${RUNTIME_CONFIG_DIR}/oai-cn5g_mmtc_${TOTAL_UES}.override.yml"
"${CN_DB_GENERATOR}" "${TOTAL_UES}" "${CN_DB_SQL}" "${CN_DB_COMPOSE_OVERLAY}"

SERVICE_LIST=(nearRT-RIC oai-gnb)
if [ "${START_XAPP}" = "1" ]; then
  SERVICE_LIST+=(xapp-rc-moni)
fi
for ue_idx in "${SAMPLE_UES[@]}"; do
  SERVICE_LIST+=("oai-nr-ue${ue_idx}")
done

echo "[INFO] Total UE target      : ${TOTAL_UES}"
echo "[INFO] Sample UE selection : ${SAMPLE_UES[*]}"
if [ -n "${EXT_DN_IP}" ]; then
  echo "[INFO] ext-dn IP           : ${EXT_DN_IP} (env override)"
else
  echo "[INFO] ext-dn IP           : auto-derive from UE TUN subnet; legacy fallback ${LEGACY_EXT_DN_IP}"
fi
echo "[INFO] Service list        : ${SERVICE_LIST[*]}"
echo "[INFO] CN DB overlay       : ${CN_DB_SQL}"

if [ "${PREPARE_ONLY}" = "1" ]; then
  echo "[INFO] Prepare-only mode active; overlay generated at ${OVERLAY_COMPOSE}"
  exit 0
fi

if [ "${RESET_CN}" = "1" ]; then
  docker compose -f "${BASE_COMPOSE}" -f "${OVERLAY_COMPOSE}" down --remove-orphans >/dev/null 2>&1 || true
  docker compose -f "${CN_COMPOSE}" -f "${CN_DB_COMPOSE_OVERLAY}" rm -sfv >/dev/null 2>&1 || true
fi

docker compose -f "${CN_COMPOSE}" -f "${CN_DB_COMPOSE_OVERLAY}" up -d
docker compose -f "${BASE_COMPOSE}" -f "${OVERLAY_COMPOSE}" up -d "${SERVICE_LIST[@]}"

echo "[INFO] Waiting ${SLEEP_AFTER_UP}s for sampled UEs to settle"
sleep "${SLEEP_AFTER_UP}"

MYSQL_LOG="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_mysql_subscribers.log"
MYSQL_CONTAINER_LOG="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_mysql.log"
AMF_LOG="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_amf.log"
UDM_LOG="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_udm.log"
AUSF_LOG="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ausf.log"
SMF_LOG="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_smf.log"
UPF_LOG="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_upf.log"
GNB_LOG="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_gnb.log"

docker logs mysql > "${MYSQL_CONTAINER_LOG}" 2>&1 || true
docker logs oai-amf > "${AMF_LOG}" 2>&1 || true
docker logs oai-udm > "${UDM_LOG}" 2>&1 || true
docker logs oai-ausf > "${AUSF_LOG}" 2>&1 || true
docker logs oai-smf > "${SMF_LOG}" 2>&1 || true
docker logs oai-upf > "${UPF_LOG}" 2>&1 || true
docker logs rfsim5g-oai-gnb_redcap > "${GNB_LOG}" 2>&1 || true

MYSQL_STATUS=$(docker inspect mysql --format '{{.State.Status}}' 2>/dev/null || echo missing)
echo "[INFO] mysql container status : ${MYSQL_STATUS}"
if [ "${MYSQL_STATUS}" != "running" ]; then
  echo "[WARN] mysql container is not running; check ${MYSQL_CONTAINER_LOG}"
  FAILURES=$((FAILURES + 1))
fi

{
  echo "-- mysql_status ${MYSQL_STATUS}"
  for ue_idx in "${SAMPLE_UES[@]}"; do
    imsi=$(printf '001010%09d' "${ue_idx}")
    echo "-- ${imsi}"
    if [ "${MYSQL_STATUS}" = "running" ]; then
      docker exec mysql mysql -uroot -plinux -D oai_db -e "
SELECT ueid FROM AuthenticationSubscription WHERE ueid = '${imsi}';
SELECT ueid FROM SessionManagementSubscriptionData WHERE ueid = '${imsi}';
" 2>&1 || true
    else
      echo "mysql container not running"
    fi
    echo
  done
} > "${MYSQL_LOG}"

for ue_idx in "${SAMPLE_UES[@]}"; do
  imsi=$(printf '001010%09d' "${ue_idx}")
  container_name="rfsim5g-oai-nr-ue${ue_idx}_redcap"
  tun_log="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_tun.log"
  ping_log="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_ping.log"
  reverse_ping_log="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_extdn_reverse_ping.log"
  ue_log="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_docker.log"
  ue_markers="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_markers.log"
  ue_state="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_state.log"
  ue_route="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_route.log"
  ue_rule="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_rule.log"
  ue_route_get="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_route_get.log"
  ue_net_pre="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_net_pre.log"
  ue_net_post="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_net_post.log"
  ue_target="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_target.log"
  gnb_pre="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_gnb_pre.log"
  gnb_post="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_gnb_post.log"
  upf_pre="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_upf_pre.log"
  upf_post="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_upf_post.log"
  extdn_pre="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_extdn_pre.log"
  extdn_post="${LOG_DIR}/mmtc_smoke_${TIMESTAMP}_ue${ue_idx}_extdn_post.log"
  ue_tun_ipv4=""
  derived_ext_dn_ip=""
  effective_ext_dn_ip=""
  target_source=""

  docker inspect "${container_name}" --format '{{json .State}}' > "${ue_state}" 2>&1 || true
  docker logs "${container_name}" > "${ue_log}" 2>&1 || true
  grep -E "Received Registration Accept|Received PDU Session Establishment Accept|Interface oaitun_ue1 successfully configured|PDU Session Establishment" "${ue_log}" > "${ue_markers}" 2>&1 || true
  docker exec "${container_name}" ip route > "${ue_route}" 2>&1 || true
  docker exec "${container_name}" ip rule show > "${ue_rule}" 2>&1 || true

  echo "[INFO] Checking ${container_name} TUN interface"
  if ! docker exec "${container_name}" ip a show dev oaitun_ue1 | tee "${tun_log}"; then
    echo "[WARN] ${container_name} has no oaitun_ue1 (IMSI ${imsi})"
    echo "[WARN] UE log markers: ${ue_markers}"
    echo "[WARN] UE state log: ${ue_state}"
    FAILURES=$((FAILURES + 1))
    continue
  fi

  ue_tun_ipv4=$(extract_tun_ipv4 "${tun_log}")
  derived_ext_dn_ip=$(derive_subnet_peer_ipv4 "${ue_tun_ipv4}")
  if [ -n "${EXT_DN_IP}" ]; then
    effective_ext_dn_ip="${EXT_DN_IP}"
    target_source="env"
  elif [ -n "${derived_ext_dn_ip}" ]; then
    effective_ext_dn_ip="${derived_ext_dn_ip}"
    target_source="tun-derived"
  else
    effective_ext_dn_ip="${LEGACY_EXT_DN_IP}"
    target_source="legacy-default"
  fi

  {
    echo "ue_tun_ipv4=${ue_tun_ipv4:-unknown}"
    echo "derived_ext_dn_ip=${derived_ext_dn_ip:-unknown}"
    echo "effective_ext_dn_ip=${effective_ext_dn_ip}"
    echo "target_source=${target_source}"
  } > "${ue_target}"

  if [ -n "${ue_tun_ipv4}" ] && ! same_slash24_subnet "${ue_tun_ipv4}" "${effective_ext_dn_ip}"; then
    echo "[WARN] ${container_name} TUN IP ${ue_tun_ipv4} is not in the same /24 subnet as ping target ${effective_ext_dn_ip}" | tee -a "${ue_target}"
  fi

  docker exec "${container_name}" ip route get "${effective_ext_dn_ip}" > "${ue_route_get}" 2>&1 || true
  capture_cmd "${ue_net_pre}" docker exec "${container_name}" sh -c '
    echo "## ip -br address"
    ip -br address || true
    echo
    echo "## ip route"
    ip route || true
    echo
    echo "## ip rule"
    ip rule show || true
    echo
    echo "## ip -s link show dev oaitun_ue1"
    ip -s link show dev oaitun_ue1 || true
    echo
    echo "## ip -s link show dev eth0"
    ip -s link show dev eth0 || true
    echo
    echo "## /proc/net/dev"
    cat /proc/net/dev || true
  '
  capture_container_snapshot "gNB-pre-ping" "rfsim5g-oai-gnb_redcap" "${gnb_pre}"
  capture_container_snapshot "UPF-pre-ping" "oai-upf" "${upf_pre}"
  capture_container_snapshot "ext-dn-pre-ping" "oai-ext-dn" "${extdn_pre}"

  echo "[INFO] Pinging ${effective_ext_dn_ip} from ${container_name} (source=${target_source}, UE IPv4=${ue_tun_ipv4:-unknown})"
  if ! docker exec "${container_name}" ping -I oaitun_ue1 -c "${PING_COUNT}" "${effective_ext_dn_ip}" | tee "${ping_log}"; then
    echo "[WARN] ${container_name} ping failed (IMSI ${imsi}, target ${effective_ext_dn_ip})"
    FAILURES=$((FAILURES + 1))
  fi

  if [ -n "${ue_tun_ipv4}" ]; then
    echo "[INFO] Reverse ping from ext-dn to ${ue_tun_ipv4}"
    if ! docker exec oai-ext-dn ping -c "${REVERSE_PING_COUNT}" "${ue_tun_ipv4}" | tee "${reverse_ping_log}"; then
      echo "[WARN] Reverse ping from ext-dn to ${ue_tun_ipv4} failed" | tee -a "${ue_target}"
      FAILURES=$((FAILURES + 1))
    fi
  fi

  capture_cmd "${ue_net_post}" docker exec "${container_name}" sh -c '
    echo "## ip -br address"
    ip -br address || true
    echo
    echo "## ip route"
    ip route || true
    echo
    echo "## ip rule"
    ip rule show || true
    echo
    echo "## ip -s link show dev oaitun_ue1"
    ip -s link show dev oaitun_ue1 || true
    echo
    echo "## ip -s link show dev eth0"
    ip -s link show dev eth0 || true
    echo
    echo "## /proc/net/dev"
    cat /proc/net/dev || true
  '
  capture_container_snapshot "gNB-post-ping" "rfsim5g-oai-gnb_redcap" "${gnb_post}"
  capture_container_snapshot "UPF-post-ping" "oai-upf" "${upf_post}"
  capture_container_snapshot "ext-dn-post-ping" "oai-ext-dn" "${extdn_post}"
done

echo "[INFO] Smoke validation completed"
echo "[INFO] Logs stored under ${LOG_DIR}"

if [ "${FAILURES}" -ne 0 ]; then
  echo "[WARN] Smoke validation reported ${FAILURES} failure(s)"
  echo "[WARN] Diagnostic logs:"
  echo "       ${MYSQL_LOG}"
  echo "       ${MYSQL_CONTAINER_LOG}"
  echo "       ${AMF_LOG}"
  echo "       ${UDM_LOG}"
  echo "       ${AUSF_LOG}"
  echo "       ${SMF_LOG}"
  echo "       ${UPF_LOG}"
  echo "       ${GNB_LOG}"
  exit 1
fi
