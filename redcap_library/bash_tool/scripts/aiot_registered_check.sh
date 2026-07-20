#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
compose_file="${repo_root}/oai-cn5g/docker-compose.yaml"

usage()
{
  cat <<'EOF'
Usage:
  aiot_registered_check.sh tag-selftest
  aiot_registered_check.sh aiotf-selftest
  aiot_registered_check.sh evidence <tag|aiotf|single_reader|two_reader|serialized_60> <log_path>
  aiot_registered_check.sh operator <validate|start|status|down>
  aiot_registered_check.sh demo
  aiot_registered_check.sh build-nrf-candidate
  aiot_registered_check.sh nrf-aiotf-conformance
  aiot_registered_check.sh nrf-legacy-baseline
  aiot_registered_check.sh aiotf-nrf-client
  aiot_registered_check.sh aiotf-naiotf-inventory
  aiot_registered_check.sh --help

Self-tests, evidence checks, validate, and status are read-only. Start/down/demo
mutate only the oai-aiotf Compose service and never remove volumes.
EOF
}

build_nrf_candidate()
{
  local source_dir="${NRF_SOURCE_DIR:-}"
  local image="${NRF_CANDIDATE_IMAGE:-oai-nrf:aiotf-ts29510-v19.6.0}"
  if [[ -z "${source_dir}" || ! -f "${source_dir}/docker/Dockerfile.nrf.ubuntu" || ! -d "${source_dir}/.git" ]]; then
    echo "AIOT_NRF_BUILD_REJECT reason=invalid_source path=${source_dir}" >&2
    return 2
  fi
  docker buildx build --load --target oai-nrf \
    --tag "${image}" \
    --file "${source_dir}/docker/Dockerfile.nrf.ubuntu" \
    --build-arg GIT_COMMIT=087f11ca-aiotf-ts29510-v19.6.0 \
    "${source_dir}"
  echo "AIOT_NRF_BUILD PASS image=${image}"
}

run_nrf_aiotf_conformance()
{
  local image="${NRF_CANDIDATE_IMAGE:-oai-nrf:aiotf-ts29510-v19.6.0}"
  local target="${NRF_CONFORMANCE_TARGET:-isolated}"
  local container="oai-nrf-aiotf-candidate"
  local network="oai-cn5g-public-net"
  local candidate_ip="192.168.70.142"
  local manage_container=1
  if [[ "${target}" = "deployed" ]]; then
    candidate_ip="192.168.70.130"
    manage_container=0
  elif [[ "${target}" != "isolated" ]]; then
    echo "AIOT_NRF_CONFORMANCE_REJECT reason=invalid_target target=${target}" >&2
    return 2
  fi
  local base_url="http://${candidate_ip}:8080"
  local aiot_id="11111111-2222-4333-8444-555555558101"
  local invalid_id="11111111-2222-4333-8444-555555558102"
  local unknown_id="11111111-2222-4333-8444-555555558103"
  local legacy_id="11111111-2222-4333-8444-555555558104"
  local valid_a valid_b invalid unknown legacy
  valid_a='{"nfInstanceId":"'"${aiot_id}"'","nfType":"AIOTF","nfStatus":"REGISTERED","heartBeatTimer":50,"ipv4Addresses":["192.168.70.210"],"aiotfInfoList":{"primary":{"aiotAreaIDList":[{"plmnId":{"mcc":"001","mnc":"01"},"aiotAreaCode":"000001"}]}}}'
  valid_b='{"nfInstanceId":"'"${aiot_id}"'","nfType":"AIOTF","nfStatus":"REGISTERED","heartBeatTimer":50,"ipv4Addresses":["192.168.70.211"],"aiotfInfoList":{"primary":{"aiotAreaIDList":[{"plmnId":{"mcc":"001","mnc":"01"},"aiotAreaCode":"000002"}]}}}'
  invalid='{"nfInstanceId":"'"${invalid_id}"'","nfType":"AIOTF","nfStatus":"REGISTERED","heartBeatTimer":50,"aiotfInfoList":{"primary":{"aiotAreaIDList":[]}}}'
  unknown='{"nfInstanceId":"'"${unknown_id}"'","nfType":"NOT_AN_NF","nfStatus":"REGISTERED","heartBeatTimer":50}'
  legacy='{"nfInstanceId":"'"${legacy_id}"'","nfType":"AMF","nfStatus":"REGISTERED","heartBeatTimer":50,"ipv4Addresses":["192.168.70.212"]}'

  cleanup_nrf_candidate()
  {
    docker rm -f "${container}" >/dev/null 2>&1 || true
  }
  cleanup_nrf_test_profiles()
  {
    local id
    for id in "${aiot_id}" "${invalid_id}" "${unknown_id}" "${legacy_id}"; do
      docker exec mysql curl --http2-prior-knowledge -sS -o /dev/null -X DELETE \
        "${base_url}/nnrf-nfm/v1/nf-instances/${id}" || true
    done
  }
  if [[ "${manage_container}" -eq 1 ]]; then
    trap cleanup_nrf_candidate EXIT

    if docker inspect "${container}" >/dev/null 2>&1; then
      if [[ "$(docker inspect --format '{{index .Config.Labels "aiotf.nrf.conformance"}}' "${container}")" != "1" ]]; then
        echo "AIOT_NRF_CONFORMANCE_REJECT reason=container_name_owned_elsewhere" >&2
        return 2
      fi
      cleanup_nrf_candidate
    fi

    docker run -d --name "${container}" \
      --label aiotf.nrf.conformance=1 \
      --network "${network}" --ip "${candidate_ip}" \
      --mount "type=bind,src=${repo_root}/oai-cn5g/conf/config.yaml,dst=/openair-nrf/etc/config.yaml,readonly" \
      "${image}" >/dev/null

    local attempt health=""
    for attempt in {1..30}; do
      health="$(docker inspect --format '{{.State.Health.Status}}' "${container}")"
      [[ "${health}" = "healthy" ]] && break
      [[ "${health}" = "unhealthy" ]] && break
      sleep 1
    done
    [[ "${health}" = "healthy" ]] || {
      docker logs "${container}" >&2 || true
      echo "AIOT_NRF_CONFORMANCE_REJECT reason=health state=${health}" >&2
      return 1
    }
  else
    trap cleanup_nrf_test_profiles EXIT
  fi

  HTTP_CODE=""
  HTTP_BODY=""
  nrf_request()
  {
    local method="$1"
    local url="$2"
    local payload="${3:-}"
    local response
    local args=(--http2-prior-knowledge -sS -X "${method}" -H 'content-type: application/json')
    [[ -n "${payload}" ]] && args+=(--data-binary "${payload}")
    response="$(docker exec mysql curl "${args[@]}" -w $'\n%{http_code}' "${url}")"
    HTTP_CODE="${response##*$'\n'}"
    HTTP_BODY="${response%$'\n'*}"
  }
  expect_code()
  {
    [[ "${HTTP_CODE}" = "$1" ]] || {
      echo "AIOT_NRF_CONFORMANCE_REJECT step=$2 expected=$1 actual=${HTTP_CODE} body=${HTTP_BODY}" >&2
      return 1
    }
    echo "AIOT_NRF_CHECK PASS step=$2 code=${HTTP_CODE}"
  }
  discover()
  {
    local target="$1"
    local area="${2:-}"
    local response
    local args=(--http2-prior-knowledge -sS -G
      --data-urlencode "target-nf-type=${target}"
      --data-urlencode "requester-nf-type=AMF")
    [[ -n "${area}" ]] && args+=(--data-urlencode "aiot-area-ids=${area}")
    response="$(docker exec mysql curl "${args[@]}" -w $'\n%{http_code}' "${base_url}/nnrf-disc/v1/nf-instances")"
    HTTP_CODE="${response##*$'\n'}"
    HTTP_BODY="${response%$'\n'*}"
  }

  local instance_url="${base_url}/nnrf-nfm/v1/nf-instances/${aiot_id}"
  nrf_request PUT "${instance_url}" "${valid_a}"
  expect_code 201 create
  nrf_request GET "${instance_url}"
  expect_code 200 read
  jq -e --arg id "${aiot_id}" '.nfInstanceId == $id and .nfType == "AIOTF" and .aiotfInfoList.primary.aiotAreaIDList[0].aiotAreaCode == "000001"' <<<"${HTTP_BODY}" >/dev/null

  nrf_request PUT "${instance_url}" "${valid_a}"
  expect_code 200 repeated_put
  nrf_request PUT "${instance_url}" "${valid_b}"
  expect_code 200 update
  nrf_request GET "${instance_url}"
  expect_code 200 update_read
  jq -e '.aiotfInfoList.primary.aiotAreaIDList[0].aiotAreaCode == "000002"' <<<"${HTTP_BODY}" >/dev/null

  nrf_request PUT "${base_url}/nnrf-nfm/v1/nf-instances/${invalid_id}" "${invalid}"
  expect_code 400 empty_area_rejected
  nrf_request GET "${base_url}/nnrf-nfm/v1/nf-instances/${invalid_id}"
  expect_code 404 empty_area_absent
  nrf_request PUT "${base_url}/nnrf-nfm/v1/nf-instances/${unknown_id}" "${unknown}"
  expect_code 400 unknown_enum_rejected
  nrf_request GET "${base_url}/nnrf-nfm/v1/nf-instances/${unknown_id}"
  expect_code 404 unknown_enum_absent

  local concurrent_a concurrent_b
  docker exec mysql curl --http2-prior-knowledge -sS -o /dev/null -X PUT -H 'content-type: application/json' --data-binary "${valid_a}" "${instance_url}" &
  concurrent_a=$!
  docker exec mysql curl --http2-prior-knowledge -sS -o /dev/null -X PUT -H 'content-type: application/json' --data-binary "${valid_b}" "${instance_url}" &
  concurrent_b=$!
  wait "${concurrent_a}"
  wait "${concurrent_b}"
  nrf_request GET "${instance_url}"
  expect_code 200 concurrent_read
  jq -e '.nfType == "AIOTF" and (.aiotfInfoList.primary.aiotAreaIDList | length == 1) and (.aiotfInfoList.primary.aiotAreaIDList[0].aiotAreaCode == "000001" or .aiotfInfoList.primary.aiotAreaIDList[0].aiotAreaCode == "000002")' <<<"${HTTP_BODY}" >/dev/null

  discover AIOTF
  expect_code 200 discovery_target_type
  jq -e --arg id "${aiot_id}" '[.nfInstances[] | select(.nfInstanceId == $id)] | length == 1' <<<"${HTTP_BODY}" >/dev/null
  local stored_area
  stored_area="$(jq -r '.aiotfInfoList.primary.aiotAreaIDList[0].aiotAreaCode' <<<"$(docker exec mysql curl --http2-prior-knowledge -sS "${instance_url}")")"
  discover AIOTF '[{"plmnId":{"mcc":"001","mnc":"01"},"aiotAreaCode":"'"${stored_area}"'"}]'
  expect_code 200 discovery_area_match
  jq -e --arg id "${aiot_id}" '[.nfInstances[] | select(.nfInstanceId == $id)] | length == 1' <<<"${HTTP_BODY}" >/dev/null
  discover AIOTF '[{"plmnId":{"mcc":"001","mnc":"01"},"aiotAreaCode":"FFFFFF"}]'
  expect_code 200 discovery_area_miss
  jq -e --arg id "${aiot_id}" '[.nfInstances[] | select(.nfInstanceId == $id)] | length == 0' <<<"${HTTP_BODY}" >/dev/null

  nrf_request PUT "${base_url}/nnrf-nfm/v1/nf-instances/${legacy_id}" "${legacy}"
  expect_code 201 legacy_amf_create
  nrf_request GET "${base_url}/nnrf-nfm/v1/nf-instances/${legacy_id}"
  expect_code 200 legacy_amf_read
  jq -e '.nfType == "AMF"' <<<"${HTTP_BODY}" >/dev/null
  discover AMF
  expect_code 200 legacy_amf_discovery
  jq -e --arg id "${legacy_id}" '[.nfInstances[] | select(.nfInstanceId == $id)] | length == 1' <<<"${HTTP_BODY}" >/dev/null

  nrf_request DELETE "${instance_url}"
  expect_code 204 delete_aiotf
  nrf_request DELETE "${base_url}/nnrf-nfm/v1/nf-instances/${legacy_id}"
  expect_code 204 delete_legacy
  nrf_request GET "${instance_url}"
  expect_code 404 deleted_absent
  discover AIOTF
  expect_code 200 discovery_empty
  jq -e --arg id "${aiot_id}" '[.nfInstances[] | select(.nfInstanceId == $id)] | length == 0' <<<"${HTTP_BODY}" >/dev/null

  if [[ "${manage_container}" -eq 1 ]]; then
    cleanup_nrf_candidate
    trap - EXIT
    if docker inspect "${container}" >/dev/null 2>&1; then
      echo "AIOT_NRF_CONFORMANCE_REJECT reason=residual_container" >&2
      return 1
    fi
  else
    trap - EXIT
  fi
  echo "AIOT_NRF_CONFORMANCE PASS target=${target} image=${image} cleanup=empty"
}

run_nrf_legacy_baseline()
{
  local base_url="http://192.168.70.130:8080"
  local legacy_id="11111111-2222-4333-8444-555555558201"
  local instance_url="${base_url}/nnrf-nfm/v1/nf-instances/${legacy_id}"
  local payload='{"nfInstanceId":"'"${legacy_id}"'","nfType":"AMF","nfStatus":"REGISTERED","heartBeatTimer":50,"ipv4Addresses":["192.168.70.212"]}'
  cleanup_legacy_profile()
  {
    docker exec mysql curl --http2-prior-knowledge -sS -o /dev/null -X DELETE "${instance_url}" || true
  }
  trap cleanup_legacy_profile EXIT

  local response code body
  response="$(docker exec mysql curl --http2-prior-knowledge -sS -X PUT -H 'content-type: application/json' --data-binary "${payload}" -w $'\n%{http_code}' "${instance_url}")"
  code="${response##*$'\n'}"
  [[ "${code}" = "201" ]] || { echo "AIOT_NRF_LEGACY_BASELINE_REJECT step=create code=${code}" >&2; return 1; }
  response="$(docker exec mysql curl --http2-prior-knowledge -sS -w $'\n%{http_code}' "${instance_url}")"
  code="${response##*$'\n'}"
  body="${response%$'\n'*}"
  [[ "${code}" = "200" ]] && jq -e '.nfType == "AMF"' <<<"${body}" >/dev/null
  response="$(docker exec mysql curl --http2-prior-knowledge -sS -G --data-urlencode 'target-nf-type=AMF' --data-urlencode 'requester-nf-type=AMF' -w $'\n%{http_code}' "${base_url}/nnrf-disc/v1/nf-instances")"
  code="${response##*$'\n'}"
  body="${response%$'\n'*}"
  [[ "${code}" = "200" ]] && jq -e --arg id "${legacy_id}" '[.nfInstances[] | select(.nfInstanceId == $id)] | length == 1' <<<"${body}" >/dev/null
  response="$(docker exec mysql curl --http2-prior-knowledge -sS -o /dev/null -X DELETE -w '%{http_code}' "${instance_url}")"
  [[ "${response}" = "204" ]] || { echo "AIOT_NRF_LEGACY_BASELINE_REJECT step=delete code=${response}" >&2; return 1; }
  trap - EXIT
  response="$(docker exec mysql curl --http2-prior-knowledge -sS -o /dev/null -w '%{http_code}' "${instance_url}")"
  [[ "${response}" = "404" ]] || { echo "AIOT_NRF_LEGACY_BASELINE_REJECT step=cleanup code=${response}" >&2; return 1; }
  echo "AIOT_NRF_LEGACY_BASELINE PASS create=201 read=200 discovery=200 delete=204 final_get=404"
}

run_aiotf_nrf_client()
{
  local image="${AIOTF_CLIENT_IMAGE:-oai-aiotf:latest}"
  local network="oai-cn5g-public-net"
  local nrf_base="http://192.168.70.130:8080"
  local instance_id="11111111-2222-4333-8444-555555558601"
  local accepted="oai-aiotf-nrf-accepted"
  local rejected="oai-aiotf-nrf-rejected"
  local timeout="oai-aiotf-nrf-timeout"
  local unavailable="oai-aiotf-nrf-unavailable"
  local containers=("${accepted}" "${rejected}" "${timeout}" "${unavailable}")

  cleanup_aiotf_nrf_client()
  {
    local container
    for container in "${containers[@]}"; do
      docker rm -f "${container}" >/dev/null 2>&1 || true
    done
    docker exec mysql curl --http2-prior-knowledge -sS -o /dev/null -X DELETE \
      "${nrf_base}/nnrf-nfm/v1/nf-instances/${instance_id}" || true
  }
  wait_marker()
  {
    local container="$1"
    local marker="$2"
    local attempt
    for attempt in {1..50}; do
      if docker logs "${container}" 2>&1 | rg -q "${marker}"; then
        return 0
      fi
      sleep 0.2
    done
    docker logs "${container}" >&2 || true
    echo "AIOTF_NRF_CLIENT_REJECT reason=marker_timeout container=${container} marker=${marker}" >&2
    return 1
  }
  start_client()
  {
    local container="$1"
    local ip="$2"
    local nrf_uri="$3"
    local nf_address="$4"
    local request_timeout="$5"
    docker run -d --name "${container}" \
      --label aiotf.nrf.client-test=1 \
      --network "${network}" --ip "${ip}" \
      "${image}" \
      --profile trusted_af_sbi --tags 1 \
      --nrf-uri "${nrf_uri}" --nf-instance-id "${instance_id}" --nf-address "${nf_address}" \
      --mcc 001 --mnc 01 --aiot-area-code 000001 \
      --nrf-timeout-ms "${request_timeout}" --nrf-retry-ms 60000 >/dev/null
  }
  nrf_code()
  {
    docker exec mysql curl --http2-prior-knowledge -sS -o /dev/null -w '%{http_code}' "$1"
  }

  trap cleanup_aiotf_nrf_client EXIT
  cleanup_aiotf_nrf_client
  docker image inspect "${image}" >/dev/null
  [[ "$(docker inspect --format '{{.State.Health.Status}}' oai-nrf)" = "healthy" ]]

  start_client "${accepted}" 192.168.70.142 http://oai-nrf:8080 192.168.70.142 1000
  wait_marker "${accepted}" 'AIOTF_NRF_REGISTRATION.*result=accepted.*code=201'
  wait_marker "${accepted}" 'AIOTF_NRF_GATE PASS.*reason=accepted'
  docker exec "${accepted}" /opt/oai-aiotf/oai-aiotf --check-live >/dev/null
  if docker exec "${accepted}" /opt/oai-aiotf/oai-aiotf --check-ready >/dev/null 2>&1; then
    echo "AIOTF_NRF_CLIENT_REJECT reason=full_readiness_claimed_without_sbi_amf" >&2
    return 1
  fi
  docker exec "${accepted}" sh -c \
    "grep -qx 'nrf_registered=1' /tmp/oai-aiotf.status && grep -qx 'sbi_listener_bound=1' /tmp/oai-aiotf.status && grep -qx 'reason=amf_dependency_unavailable' /tmp/oai-aiotf.status"
  [[ "$(docker inspect "${accepted}" --format '{{json .NetworkSettings.Networks}}' | jq 'keys == ["oai-cn5g-public-net"]')" = "true" ]]
  local instance_url="${nrf_base}/nnrf-nfm/v1/nf-instances/${instance_id}"
  [[ "$(nrf_code "${instance_url}")" = "200" ]]
  docker exec mysql curl --http2-prior-knowledge -sS "${instance_url}" \
    | jq -e --arg id "${instance_id}" \
      '.nfInstanceId == $id and .nfType == "AIOTF" and .aiotfInfoList.primary.aiotAreaIDList[0].aiotAreaCode == "000001"' \
      >/dev/null
  docker exec mysql curl --http2-prior-knowledge -sS -G \
    --data-urlencode target-nf-type=AIOTF --data-urlencode requester-nf-type=AIOTF \
    --data-urlencode 'aiot-area-ids=[{"plmnId":{"mcc":"001","mnc":"01"},"aiotAreaCode":"000001"}]' \
    "${nrf_base}/nnrf-disc/v1/nf-instances" \
    | jq -e --arg id "${instance_id}" '[.nfInstances[] | select(.nfInstanceId == $id)] | length == 1' >/dev/null
  docker logs "${accepted}" 2>&1 \
    | rg 'AIOTF_NRF_(REGISTRATION|READBACK|DISCOVERY|GATE)|AIOTF_SERVICE_(LIVE|READY)'
  echo "AIOTF_NRF_CLIENT_CHECK PASS step=accepted_registration_readback_discovery"

  docker kill --signal KILL "${accepted}" >/dev/null
  docker rm "${accepted}" >/dev/null
  [[ "$(nrf_code "${instance_url}")" = "200" ]]
  start_client "${accepted}" 192.168.70.142 http://oai-nrf:8080 192.168.70.142 1000
  wait_marker "${accepted}" 'AIOTF_NRF_REGISTRATION.*result=accepted.*code=200'
  wait_marker "${accepted}" 'AIOTF_NRF_GATE PASS.*reason=accepted'
  docker exec mysql curl --http2-prior-knowledge -sS -G \
    --data-urlencode target-nf-type=AIOTF --data-urlencode requester-nf-type=AIOTF \
    "${nrf_base}/nnrf-disc/v1/nf-instances" \
    | jq -e --arg id "${instance_id}" '[.nfInstances[] | select(.nfInstanceId == $id)] | length == 1' >/dev/null
  docker logs "${accepted}" 2>&1 | rg 'AIOTF_NRF_(REGISTRATION|READBACK|DISCOVERY|GATE)'
  echo "AIOTF_NRF_CLIENT_CHECK PASS step=duplicate_instance_restart"

  docker stop --time 5 "${accepted}" >/dev/null
  wait_marker "${accepted}" 'AIOTF_NRF_DEREGISTRATION.*result=accepted.*code=204'
  docker logs "${accepted}" 2>&1 | rg 'AIOTF_NRF_DEREGISTRATION'
  docker rm "${accepted}" >/dev/null
  [[ "$(nrf_code "${instance_url}")" = "404" ]]
  echo "AIOTF_NRF_CLIENT_CHECK PASS step=deregistration"

  start_client "${rejected}" 192.168.70.143 http://oai-nrf:8080/invalid 192.168.70.143 1000
  wait_marker "${rejected}" 'AIOTF_NRF_GATE REJECT.*reason=http_rejected'
  docker logs "${rejected}" 2>&1 | rg 'AIOTF_NRF_GATE REJECT'
  docker exec "${rejected}" /opt/oai-aiotf/oai-aiotf --check-live >/dev/null
  docker rm -f "${rejected}" >/dev/null
  echo "AIOTF_NRF_CLIENT_CHECK PASS step=rejection"

  start_client "${timeout}" 192.168.70.144 http://192.168.70.254:8080 192.168.70.144 200
  wait_marker "${timeout}" 'AIOTF_NRF_GATE REJECT.*reason=timeout.*curl_exit=28'
  docker logs "${timeout}" 2>&1 | rg 'AIOTF_NRF_GATE REJECT'
  docker exec "${timeout}" /opt/oai-aiotf/oai-aiotf --check-live >/dev/null
  docker rm -f "${timeout}" >/dev/null
  echo "AIOTF_NRF_CLIENT_CHECK PASS step=timeout"

  start_client "${unavailable}" 192.168.70.145 http://127.0.0.1:9 192.168.70.145 1000
  wait_marker "${unavailable}" 'AIOTF_NRF_GATE REJECT.*reason=unavailable'
  docker logs "${unavailable}" 2>&1 | rg 'AIOTF_NRF_GATE REJECT'
  docker exec "${unavailable}" /opt/oai-aiotf/oai-aiotf --check-live >/dev/null
  docker rm -f "${unavailable}" >/dev/null
  echo "AIOTF_NRF_CLIENT_CHECK PASS step=nrf_unavailable"

  trap - EXIT
  cleanup_aiotf_nrf_client
  [[ "$(nrf_code "${instance_url}")" = "404" ]]
  echo "AIOTF_NRF_CLIENT PASS accepted=1 rejection=1 timeout=1 duplicate=1 restart=1 deregistration=1 unavailable=1 cleanup=empty"
}

run_aiotf_naiotf_inventory()
{
  local image="${AIOTF_CLIENT_IMAGE:-oai-aiotf:latest}"
  local network="oai-cn5g-public-net"
  local callback_backend="oai-aiotf-naiotf-callback-backend"
  local callback_proxy="oai-aiotf-naiotf-callback-proxy"
  local service="oai-aiotf-naiotf-service"
  local instance_id="11111111-2222-4333-8444-555555558701"
  local instance_url="http://192.168.70.130:8080/nnrf-nfm/v1/nf-instances/${instance_id}"
  local service_url="http://192.168.70.148:8080/naiotf-aiot/v1/request-inv"
  local callback_uri="http://192.168.70.147:39090/callback"
  local containers=("${service}" "${callback_proxy}" "${callback_backend}")

  cleanup_naiotf()
  {
    local container
    for container in "${containers[@]}"; do
      docker rm -f "${container}" >/dev/null 2>&1 || true
    done
    docker exec mysql curl --http2-prior-knowledge -sS -o /dev/null -X DELETE "${instance_url}" || true
  }
  wait_log_count()
  {
    local container="$1"
    local marker="$2"
    local expected="$3"
    local attempt count
    for attempt in {1..80}; do
      count="$(docker logs "${container}" 2>&1 | rg -c "${marker}" || true)"
      [[ "${count}" -ge "${expected}" ]] && return 0
      sleep 0.25
    done
    docker logs "${container}" >&2 || true
    echo "AIOTF_NAIOTF_RUNTIME_REJECT reason=marker_timeout container=${container} marker=${marker}" >&2
    return 1
  }
  start_service()
  {
    docker run -d --name "${service}" \
      --label aiotf.naiotf.inventory-test=1 \
      --network "${network}" --ip 192.168.70.148 \
      "${image}" \
      --profile trusted_af_sbi --tags "${all_tags}" \
      --nrf-uri http://oai-nrf:8080 --nf-instance-id "${instance_id}" --nf-address 192.168.70.148 \
      --mcc 001 --mnc 01 --aiot-area-code 000001 \
      --nrf-timeout-ms 1000 --nrf-retry-ms 60000 --timeout-ms 1000 \
      --sbi-address 0.0.0.0 --sbi-port 8080 --trusted-af-id trusted-af >/dev/null
    wait_log_count "${service}" 'AIOTF_NAIOTF_LISTENER PASS' 1
  }
  naiotf_request()
  {
    local payload="$1"
    local response
    response="$(docker exec mysql curl --http2-prior-knowledge -sS \
      -H 'content-type: application/json' --data-binary "${payload}" \
      -w $'\n%{http_code}' "${service_url}")"
    NAIOTF_CODE="${response##*$'\n'}"
    NAIOTF_BODY="${response%$'\n'*}"
  }

  trap cleanup_naiotf EXIT
  cleanup_naiotf
  docker image inspect "${image}" >/dev/null
  [[ "$(docker inspect --format '{{.State.Health.Status}}' oai-nrf)" = "healthy" ]]

  local callback_code
  callback_code='from http.server import BaseHTTPRequestHandler,HTTPServer
class H(BaseHTTPRequestHandler):
 def do_POST(self):
  size=int(self.headers.get("content-length","0")); data=self.rfile.read(size); print("AIOTF_NAIOTF_CALLBACK "+data.decode(),flush=True); self.send_response(204); self.end_headers()
 def log_message(self,*args): pass
HTTPServer(("0.0.0.0",39091),H).serve_forever()'
  docker run -d --name "${callback_backend}" \
    --label aiotf.naiotf.inventory-test=1 \
    --network "${network}" --ip 192.168.70.146 \
    --entrypoint python3 "${image}" -c "${callback_code}" >/dev/null
  docker run -d --name "${callback_proxy}" \
    --label aiotf.naiotf.inventory-test=1 \
    --network "${network}" --ip 192.168.70.147 \
    --entrypoint nghttpx "${image}" \
    '--frontend=0.0.0.0,39090;no-tls' --backend=192.168.70.146,39091 \
    --backend-address-family=IPv4 --log-level=WARN --accesslog-file=/dev/null >/dev/null

  local all_tags=""
  local device_list=""
  local tag_id encoded
  for tag_id in {1..60}; do
    all_tags+="${all_tags:+,}${tag_id}"
    encoded="$(printf '%08x' "${tag_id}" | xxd -r -p | base64 -w0)"
    device_list+="${device_list:+,}\"${encoded}\""
  done
  local one='["AAAAAQ=="]'
  local duplicate='["AAAAAQ==","AAAAAQ=="]'
  local sixty="[${device_list}]"
  local sixty_one="[${device_list},\"AAAAPQ==\"]"
  local payload
  local NAIOTF_CODE="" NAIOTF_BODY=""

  start_service
  payload='{"afId":"other-af","targetDevices":{"devices":'"${one}"'},"notifUri":"'"${callback_uri}"'"}'
  naiotf_request "${payload}"
  [[ "${NAIOTF_CODE}" = "403" ]]
  payload='{"afId":"trusted-af","targetDevices":{"devices":[]},"notifUri":"'"${callback_uri}"'"}'
  naiotf_request "${payload}"
  [[ "${NAIOTF_CODE}" = "400" ]]
  payload='{"afId":"trusted-af","targetDevices":{"devices":'"${duplicate}"'},"notifUri":"'"${callback_uri}"'"}'
  naiotf_request "${payload}"
  [[ "${NAIOTF_CODE}" = "400" ]]
  payload='{"afId":"trusted-af","targetDevices":{"devices":'"${sixty_one}"'},"notifUri":"'"${callback_uri}"'"}'
  naiotf_request "${payload}"
  [[ "${NAIOTF_CODE}" = "400" ]]
  echo "AIOTF_NAIOTF_RUNTIME_CHECK PASS step=rejection_boundaries zero=400 duplicate=400 tags61=400 unauthorized=403"

  payload='{"afId":"trusted-af","targetDevices":{"devices":'"${one}"'},"timeInterval":1,"notifUri":"'"${callback_uri}"'"}'
  naiotf_request "${payload}"
  [[ "${NAIOTF_CODE}" = "200" ]]
  local first_trans_id
  first_trans_id="$(jq -er '.transId' <<<"${NAIOTF_BODY}")"
  wait_log_count "${callback_backend}" 'AIOTF_NAIOTF_CALLBACK.*NO_SUCC_INV_RESP' 1
  wait_log_count "${service}" 'AIOTF_NAIOTF_NOTIFY PASS' 1
  echo "AIOTF_NAIOTF_RUNTIME_CHECK PASS step=one_tag_callback trans_id=${first_trans_id}"

  payload='{"afId":"trusted-af","targetDevices":{"devices":'"${sixty}"'},"numDevices":60,"timeInterval":1,"notifUri":"'"${callback_uri}"'"}'
  naiotf_request "${payload}"
  [[ "${NAIOTF_CODE}" = "200" ]]
  wait_log_count "${callback_backend}" 'AIOTF_NAIOTF_CALLBACK.*NO_SUCC_INV_RESP' 2
  wait_log_count "${service}" 'AIOTF_NAIOTF_NOTIFY PASS' 2
  echo "AIOTF_NAIOTF_RUNTIME_CHECK PASS step=sixty_tag_callback"

  docker stop --time 5 "${service}" >/dev/null
  docker rm "${service}" >/dev/null
  start_service
  payload='{"afId":"trusted-af","targetDevices":{"devices":'"${one}"'},"timeInterval":1,"notifUri":"'"${callback_uri}"'"}'
  naiotf_request "${payload}"
  [[ "${NAIOTF_CODE}" = "200" ]]
  local restarted_trans_id
  restarted_trans_id="$(jq -er '.transId' <<<"${NAIOTF_BODY}")"
  [[ "${restarted_trans_id}" != "${first_trans_id}" ]]
  wait_log_count "${callback_backend}" 'AIOTF_NAIOTF_CALLBACK.*NO_SUCC_INV_RESP' 3
  wait_log_count "${service}" 'AIOTF_NAIOTF_NOTIFY PASS' 1
  docker logs "${service}" 2>&1 | rg 'AIOTF_(NAIOTF|NRF|SERVICE_)'
  docker logs "${callback_backend}" 2>&1 | rg 'AIOTF_NAIOTF_CALLBACK'
  echo "AIOTF_NAIOTF_RUNTIME_CHECK PASS step=restart_state first=${first_trans_id} restarted=${restarted_trans_id}"

  trap - EXIT
  cleanup_naiotf
  local container
  for container in "${containers[@]}"; do
    if docker inspect "${container}" >/dev/null 2>&1; then
      echo "AIOTF_NAIOTF_RUNTIME_REJECT reason=residual_container container=${container}" >&2
      return 1
    fi
  done
  echo "AIOTF_NAIOTF_RUNTIME PASS protocol=h2c tags=0,1,60,61 auth=rejected callback=204 restart=unique cleanup=empty"
}

require_executable()
{
  if [[ ! -x "$1" ]]; then
    echo "AIOT_REGISTERED_CHECK missing_executable=$1" >&2
    return 2
  fi
}

check_evidence()
{
  if [[ $# -ne 2 ]]; then
    usage >&2
    return 2
  fi

  local kind="$1"
  local resolved
  resolved="$(realpath -e "$2")" || return 2
  case "${resolved}" in
    "${repo_root}"/test_log/*) ;;
    *)
      echo "AIOT_EVIDENCE_REJECT reason=path_outside_test_log path=${resolved}" >&2
      return 2
      ;;
  esac

  local markers=()
  case "${kind}" in
    tag) markers=("AIOT_T2_SELF_TEST PASS") ;;
    aiotf) markers=("AIOTF_INVENTORY_TEST PASS") ;;
    single_reader) markers=("AIOT_T2_BACKSCATTER" "AIOT_T2_D2R_CRC_OK" "AIOT_T2_UE_REPORT_SENT") ;;
    two_reader) markers=("AIOT_T2_R2D_SENT" "AIOT_T2_D2R_CRC_OK" "bytes=40") ;;
    serialized_60) markers=("AIOTF_SERIALIZED_60_TAGS" "AIOTF_INVENTORY_TEST PASS") ;;
    *)
      echo "AIOT_EVIDENCE_REJECT reason=unknown_kind kind=${kind}" >&2
      return 2
      ;;
  esac

  local marker
  for marker in "${markers[@]}"; do
    if ! rg -F -q -- "${marker}" "${resolved}"; then
      echo "AIOT_EVIDENCE_REJECT reason=missing_marker marker=${marker} path=${resolved}" >&2
      return 1
    fi
  done
  echo "AIOT_EVIDENCE_CHECK PASS kind=${kind} path=${resolved}"
}

operator_validate()
{
  [[ "${AIOTF_TRANSPORT_PROFILE:-experimental_n6}" = "experimental_n6" ]] || {
    echo "AIOT_OPERATOR_REJECT reason=unsupported_profile profile=${AIOTF_TRANSPORT_PROFILE}" >&2
    return 2
  }
  local baseline_services aiot_services
  baseline_services="$(docker compose -f "${compose_file}" config --services)"
  aiot_services="$(docker compose -f "${compose_file}" --profile aiot config --services)"
  if rg -x -q 'oai-aiotf' <<<"${baseline_services}" || ! rg -x -q 'oai-aiotf' <<<"${aiot_services}"; then
    echo "AIOT_OPERATOR_REJECT reason=compose_profile_boundary" >&2
    return 1
  fi
  docker compose -f "${compose_file}" --profile aiot config >/dev/null
  echo "AIOT_OPERATOR_VALIDATE PASS profile=experimental_n6 baseline_aiotf=0 enabled_aiotf=1"
}

operator_start()
{
  operator_validate
  docker compose -f "${compose_file}" --profile aiot up -d --no-deps oai-aiotf
  echo "AIOT_OPERATOR_START PASS profile=experimental_n6 service=oai-aiotf"
}

operator_status()
{
  docker compose -f "${compose_file}" --profile aiot ps oai-aiotf
  if docker compose -f "${compose_file}" --profile aiot ps --status running --services | rg -x -q 'oai-aiotf'; then
    echo "AIOT_OPERATOR_STATUS PASS profile=experimental_n6 service=oai-aiotf state=running"
  else
    echo "AIOT_OPERATOR_STATUS profile=experimental_n6 service=oai-aiotf state=stopped"
  fi
}

operator_down()
{
  docker compose -f "${compose_file}" --profile aiot stop oai-aiotf >/dev/null
  docker compose -f "${compose_file}" --profile aiot rm -f -s oai-aiotf >/dev/null
  echo "AIOT_OPERATOR_DOWN PASS profile=experimental_n6 service=oai-aiotf volumes=preserved"
}

run_demo()
{
  export AIOTF_TAGS=25
  export AIOTF_PENDING_CONTEXT=25:diversity:9:1:1:10:5
  export AIOTF_TIMEOUT_MS=60000
  trap operator_down EXIT
  operator_start

  local attempt running=0
  for attempt in {1..20}; do
    if docker compose -f "${compose_file}" --profile aiot ps --status running --services | rg -x -q 'oai-aiotf'; then
      running=1
      break
    fi
    sleep 1
  done
  [[ "${running}" -eq 1 ]] || {
    echo "AIOT_T2_DEMO_REJECT reason=service_not_running" >&2
    return 1
  }

  python3 -c 'import socket,struct
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
for reader,slot in ((2,5),(1,5),(1,6)):
    s.sendto(struct.pack("!IBBHIIII16s",0x41494f54,1,1,1,reader,25,10,slot,bytes([0x11])),("127.0.0.1",36900))'
  sleep 1
  local logs
  logs="$(docker logs oai-aiotf 2>&1)"
  printf '%s\n' "${logs}"
  rg -q 'AIOTF_DIAGNOSTIC_ASSOCIATED profile=experimental_n6.*arbitration=0' <<<"${logs}"
  rg -q 'AIOTF_DIAGNOSTIC_ASSOCIATED profile=experimental_n6.*arbitration=1' <<<"${logs}"
  rg -q 'AIOTF_DIAGNOSTIC_REJECT profile=experimental_n6 reason=no_pending_context' <<<"${logs}"
  echo "AIOT_T2_DEMO PASS profile=experimental_n6 first_valid=1 duplicate=1 rejected=1"
}

case "${1:---help}" in
  tag-selftest)
    [[ $# -eq 1 ]] || { usage >&2; exit 2; }
    tag_bin="${repo_root}/cmake_targets/ran_build/build/radio/rfsimulator/replay_node"
    require_executable "${tag_bin}"
    exec "${tag_bin}" --aiot-tag-self-test
    ;;
  aiotf-selftest)
    [[ $# -eq 1 ]] || { usage >&2; exit 2; }
    aiotf_test_bin="${repo_root}/cmake_targets/ran_build/build/openair3/AIOTF/test_aiotf_inventory"
    require_executable "${aiotf_test_bin}"
    exec "${aiotf_test_bin}"
    ;;
  evidence)
    shift
    check_evidence "$@"
    ;;
  operator)
    [[ $# -eq 2 ]] || { usage >&2; exit 2; }
    case "$2" in
      validate) operator_validate ;;
      start) operator_start ;;
      status) operator_status ;;
      down) operator_down ;;
      *) usage >&2; exit 2 ;;
    esac
    ;;
  demo)
    [[ $# -eq 1 ]] || { usage >&2; exit 2; }
    run_demo
    ;;
  build-nrf-candidate)
    [[ $# -eq 1 ]] || { usage >&2; exit 2; }
    build_nrf_candidate
    ;;
  nrf-aiotf-conformance)
    [[ $# -eq 1 ]] || { usage >&2; exit 2; }
    run_nrf_aiotf_conformance
    ;;
  nrf-legacy-baseline)
    [[ $# -eq 1 ]] || { usage >&2; exit 2; }
    run_nrf_legacy_baseline
    ;;
  aiotf-nrf-client)
    [[ $# -eq 1 ]] || { usage >&2; exit 2; }
    run_aiotf_nrf_client
    ;;
  aiotf-naiotf-inventory)
    [[ $# -eq 1 ]] || { usage >&2; exit 2; }
    run_aiotf_naiotf_inventory
    ;;
  -h|--help)
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
