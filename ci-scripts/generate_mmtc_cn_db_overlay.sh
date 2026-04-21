#!/usr/bin/env bash

set -euo pipefail

TOTAL_UES="${1:-64}"
OUTPUT_SQL="${2:-}"
OUTPUT_COMPOSE="${3:-}"

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/..")
RUNTIME_DIR="${REPO_ROOT}/test_log/runtime_configs"

if ! [[ "${TOTAL_UES}" =~ ^[0-9]+$ ]]; then
  echo "TOTAL_UES must be an integer, got: ${TOTAL_UES}" >&2
  exit 1
fi

mkdir -p "${RUNTIME_DIR}"

if [ -z "${OUTPUT_SQL}" ]; then
  OUTPUT_SQL="${RUNTIME_DIR}/oai_db_mmtc_${TOTAL_UES}.sql"
fi

if [ -z "${OUTPUT_COMPOSE}" ]; then
  OUTPUT_COMPOSE="${RUNTIME_DIR}/oai-cn5g_mmtc_${TOTAL_UES}.override.yml"
fi

emit_auth_rows() {
  local idx imsi suffix
  for ((idx=1; idx<=TOTAL_UES; idx++)); do
    imsi=$(printf '001010%09d' "${idx}")
    if [ "${idx}" -lt "${TOTAL_UES}" ]; then
      suffix=","
    else
      suffix=""
    fi
    printf "('%s', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\\\"sqn\\\": \\\"000000000000\\\", \\\"sqnScheme\\\": \\\"NON_TIME_BASED\\\", \\\"lastIndexes\\\": {\\\"ausf\\\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '%s')%s\n" \
      "${imsi}" "${imsi}" "${suffix}"
  done
}

emit_session_rows() {
  local idx imsi suffix ue_ip_octet
  for ((idx=1; idx<=TOTAL_UES; idx++)); do
    imsi=$(printf '001010%09d' "${idx}")
    ue_ip_octet=$((idx + 1))
    if [ "${idx}" -lt "${TOTAL_UES}" ]; then
      suffix=","
    else
      suffix=""
    fi
    printf "('%s', '00101', '{\\\"sst\\\": 1, \\\"sd\\\": \\\"FFFFFF\\\"}', '{\\\"oai\\\":{\\\"pduSessionTypes\\\":{ \\\"defaultSessionType\\\": \\\"IPV4\\\"},\\\"sscModes\\\": {\\\"defaultSscMode\\\": \\\"SSC_MODE_1\\\"},\\\"5gQosProfile\\\": {\\\"5qi\\\": 6,\\\"arp\\\":{\\\"priorityLevel\\\": 15,\\\"preemptCap\\\": \\\"NOT_PREEMPT\\\",\\\"preemptVuln\\\":\\\"PREEMPTABLE\\\"},\\\"priorityLevel\\\":1},\\\"sessionAmbr\\\":{\\\"uplink\\\":\\\"1000Mbps\\\", \\\"downlink\\\":\\\"1000Mbps\\\"},\\\"staticIpAddress\\\":[{\\\"ipv4Addr\\\": \\\"10.0.0.%d\\\"}]},\\\"ims\\\":{\\\"pduSessionTypes\\\":{ \\\"defaultSessionType\\\": \\\"IPV4V6\\\"},\\\"sscModes\\\": {\\\"defaultSscMode\\\": \\\"SSC_MODE_1\\\"},\\\"5gQosProfile\\\": {\\\"5qi\\\": 2,\\\"arp\\\":{\\\"priorityLevel\\\": 15,\\\"preemptCap\\\": \\\"NOT_PREEMPT\\\",\\\"preemptVuln\\\":\\\"PREEMPTABLE\\\"},\\\"priorityLevel\\\":1},\\\"sessionAmbr\\\":{\\\"uplink\\\":\\\"1000Mbps\\\", \\\"downlink\\\":\\\"1000Mbps\\\"}}}')%s\n" \
      "${imsi}" "${ue_ip_octet}" "${suffix}"
  done
}

cat > "${OUTPUT_SQL}" <<'EOF'
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;

-- The CN baseline mounted by doc/tutorial_resources/oai-cn5g/docker-compose.yaml
-- defines AuthenticationSubscription and SessionManagementSubscriptionData,
-- but it does not define the legacy `users` table from ci-scripts/yaml_files/5g_rfsimulator/oai_db.sql.
-- Keep this overlay aligned with the actual CN schema to avoid failing MySQL init.

EOF

if [ "${TOTAL_UES}" -ge 1 ]; then
  cat >> "${OUTPUT_SQL}" <<'EOF'
INSERT INTO `AuthenticationSubscription`
(`ueid`, `authenticationMethod`, `encPermanentKey`, `protectionParameterId`, `sequenceNumber`, `authenticationManagementField`, `algorithmId`, `encOpcKey`, `encTopcKey`, `vectorGenerationInHss`, `n5gcAuthMethod`, `rgAuthenticationInd`, `supi`)
VALUES
EOF
  emit_auth_rows >> "${OUTPUT_SQL}"

  cat >> "${OUTPUT_SQL}" <<'EOF'
ON DUPLICATE KEY UPDATE
  authenticationMethod=VALUES(authenticationMethod),
  encPermanentKey=VALUES(encPermanentKey),
  protectionParameterId=VALUES(protectionParameterId),
  sequenceNumber=VALUES(sequenceNumber),
  authenticationManagementField=VALUES(authenticationManagementField),
  algorithmId=VALUES(algorithmId),
  encOpcKey=VALUES(encOpcKey),
  supi=VALUES(supi);

INSERT INTO `SessionManagementSubscriptionData`
(`ueid`, `servingPlmnid`, `singleNssai`, `dnnConfigurations`)
VALUES
EOF
  emit_session_rows >> "${OUTPUT_SQL}"

  cat >> "${OUTPUT_SQL}" <<'EOF'
ON DUPLICATE KEY UPDATE
  singleNssai=VALUES(singleNssai),
  dnnConfigurations=VALUES(dnnConfigurations);

EOF
fi

cat >> "${OUTPUT_SQL}" <<'EOF'
COMMIT;
EOF

cat > "${OUTPUT_COMPOSE}" <<EOF
services:
  mysql:
    volumes:
      - ${OUTPUT_SQL}:/docker-entrypoint-initdb.d/zz_oai_db_mmtc.sql:ro
EOF

echo "Generated CN DB SQL overlay: ${OUTPUT_SQL}"
echo "Generated CN compose overlay: ${OUTPUT_COMPOSE}"
