#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(realpath "${SCRIPT_DIR}/../../..")
BASE_SQL="${REPO_ROOT}/oai-cn5g/database/oai_db.sql"
SEED_SQL="${REPO_ROOT}/oai-cn5g/database/oai_db_mmtc_56.sql"
CONTAINER_NAME="redcap-cn5g-seed-check-$$"

cleanup()
{
  docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

for path in "${BASE_SQL}" "${SEED_SQL}"; do
  if [ ! -f "${path}" ]; then
    echo "[FAIL] Missing SQL input: ${path}" >&2
    exit 1
  fi
done

docker run --detach --pull=never \
  --name "${CONTAINER_NAME}" \
  --env MYSQL_DATABASE=oai_db \
  --env MYSQL_USER=test \
  --env MYSQL_PASSWORD=test \
  --env MYSQL_ROOT_PASSWORD=linux \
  --volume "${BASE_SQL}:/docker-entrypoint-initdb.d/oai_db.sql:ro" \
  --volume "${SEED_SQL}:/docker-entrypoint-initdb.d/zz_oai_db_mmtc_56.sql:ro" \
  mysql:8.0 >/dev/null

query()
{
  docker exec "${CONTAINER_NAME}" \
    mysql --batch --skip-column-names --user=root --password=linux oai_db --execute "$1" 2>/dev/null
}

ready=0
for _ in $(seq 1 60); do
  if count=$(query "SELECT COUNT(DISTINCT ueid) FROM SessionManagementSubscriptionData WHERE ueid BETWEEN '001010000000001' AND '001010000000056';") \
     && [ "${count}" = "56" ]; then
    ready=1
    break
  fi
  sleep 2
done

if [ "${ready}" -ne 1 ]; then
  echo "[FAIL] MySQL did not complete clean initialization." >&2
  docker logs "${CONTAINER_NAME}" >&2 || true
  exit 1
fi

auth_count=$(query "SELECT COUNT(DISTINCT ueid) FROM AuthenticationSubscription WHERE ueid BETWEEN '001010000000001' AND '001010000000056';")
session_count=$(query "SELECT COUNT(DISTINCT ueid) FROM SessionManagementSubscriptionData WHERE ueid BETWEEN '001010000000001' AND '001010000000056';")
boundary_count=$(query "SELECT (SELECT COUNT(*) FROM AuthenticationSubscription WHERE ueid IN ('001010000000001','001010000000056')) + (SELECT COUNT(*) FROM SessionManagementSubscriptionData WHERE ueid IN ('001010000000001','001010000000056'));")
ue1_ip=$(query "SELECT JSON_UNQUOTE(JSON_EXTRACT(dnnConfigurations, '$.oai.staticIpAddress[0].ipv4Addr')) FROM SessionManagementSubscriptionData WHERE ueid='001010000000001';")
ue56_ip=$(query "SELECT JSON_UNQUOTE(JSON_EXTRACT(dnnConfigurations, '$.oai.staticIpAddress[0].ipv4Addr')) FROM SessionManagementSubscriptionData WHERE ueid='001010000000056';")
session_above_56=$(query "SELECT COUNT(*) FROM SessionManagementSubscriptionData WHERE ueid REGEXP '^001010[0-9]{9}$' AND CAST(RIGHT(ueid, 9) AS UNSIGNED) > 56;")

if [ "${auth_count}" != "56" ] \
   || [ "${session_count}" != "56" ] \
   || [ "${boundary_count}" != "4" ] \
   || [ "${ue1_ip}" != "10.0.0.2" ] \
   || [ "${ue56_ip}" != "10.0.0.57" ] \
   || [ "${session_above_56}" != "0" ]; then
  echo "[FAIL] auth=${auth_count} session=${session_count} boundaries=${boundary_count} ue1_ip=${ue1_ip} ue56_ip=${ue56_ip} session_above_56=${session_above_56}" >&2
  exit 1
fi

echo "[PASS] clean_init=1 auth_supported=56 session_supported=56 boundary_rows=4 ue1_ip=10.0.0.2 ue56_ip=10.0.0.57 session_above_56=0"
