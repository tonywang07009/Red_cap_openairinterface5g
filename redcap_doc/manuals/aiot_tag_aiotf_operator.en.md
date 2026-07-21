# A-IoT Tag and AIOTF Operator Guide

English | [繁體中文](./aiot_tag_aiotf_operator.zh-TW.md)

English route | Build the file and function context first with the two-week [繁體中文 course](./aiot_redcap_to_aiotf_two_week_course.zh-TW.md)

## Scope

Use the normal operator and demonstration commands only for the disabled-by-default `experimental_n6` diagnostic profile. Separate AIOTF NRF-client and Naiotf Inventory gates do not validate AMF/NGAP/RRC transport, NEF exposure, physical RF, or 3GPP conformance.

## Build

Use the registered rebuild owner after changing AIOTF, UE, RFsim, or Docker source:

```bash
redcap_interface/bash_library/fc_rebuild_local_oai_images.sh
```

The build produces `ran-build:latest`, `oai-aiotf:latest`, `oai-gnb:latest`, and `oai-nr-ue:latest`. Track this long command in `task_log/tasks.json` and read the retained build log before marking it passed.

## Configure

| Input | Default | Rule |
|---|---|---|
| `AIOTF_TRANSPORT_PROFILE` | `experimental_n6` | Other values fail closed; no fallback |
| `AIOTF_TAGS` | `1,2,...,60` | Unique Tag IDs 1-60 |
| `AIOTF_PENDING_CONTEXT` | `25:diversity:9:1:1:10:5` | `TAG:normal|diversity:CORRELATION:SESSION:EPOCH:FRAME:SLOT` |
| `AIOTF_TIMEOUT_MS` | `60000` | Positive local diagnostic timeout; not a 3GPP timer |

The pending Tag must appear in `AIOTF_TAGS`. Duplicate Tag/frame/slot contexts, stale binding epochs, duplicate session IDs, empty Tags, and out-of-range values fail before the UDP listener starts.

## Operate

```bash
./mmtc.menu.bash aiot validate
./mmtc.menu.bash aiot start
./mmtc.menu.bash aiot status
./mmtc.menu.bash aiot down
```

| Command | Mutation | Required result |
|---|---|---|
| `validate` | None | Baseline excludes AIOTF; profile `aiot` includes it; Compose renders |
| `start` | Starts only `oai-aiotf` | `AIOT_OPERATOR_START PASS` |
| `status` | None | Reports `running` or `stopped` |
| `down` | Stops/removes only `oai-aiotf` | `AIOT_OPERATOR_DOWN PASS ... volumes=preserved` |

`down` is idempotent. It never passes `-v` and does not stop NRF, AMF, SMF, UPF, UDM, UDR, AUSF, MySQL, IMS, ext-DN, gNB, or UEs.

## Demonstrate

```bash
redcap_interface/mmtc.display.bash aiot-t2
```

The fixed demonstration starts Tag 25 in diversity pending context, sends three loopback diagnostic records, and then removes AIOTF:

| Record | Expected marker |
|---|---|
| Reader 2, frame 10, slot 5 | `AIOTF_DIAGNOSTIC_ASSOCIATED ... arbitration=0` |
| Reader 1, frame 10, slot 5 | `AIOTF_DIAGNOSTIC_ASSOCIATED ... arbitration=1` |
| Reader 1, frame 10, slot 6 | `AIOTF_DIAGNOSTIC_REJECT ... reason=no_pending_context` |

The final marker is `AIOT_T2_DEMO PASS profile=experimental_n6 first_valid=1 duplicate=1 rejected=1`. A trap invokes the registered AIOTF `down` operation on success or failure.

## Registry and skill

| Owner | Entry |
|---|---|
| Bash Tool Registry | `redcap_library/bash_tool/registry.json` |
| Registered wrapper | `redcap_library/bash_tool/scripts/aiot_registered_check.sh` |
| Workflow skill | `redcap_library/skills/tag_aiotf_workflow/SKILL.md` |

The skill validates Tags, payload length, reader mode, wake window, reader handles, evidence path, and exact profile. It invokes only registry dependencies. Requests for unavailable `trusted_af_sbi` or `third_party_af_nef` return `missing_capability`; they are never downgraded to N6.

## Self-tests and retained evidence

```bash
redcap_library/bash_tool/scripts/aiot_registered_check.sh tag-selftest
redcap_library/bash_tool/scripts/aiot_registered_check.sh aiotf-selftest
redcap_library/bash_tool/scripts/aiot_registered_check.sh evidence aiotf \
  test_log/compiler_logs/aiotf_evidence_ladder_selftests_2026-07-20_13-39-00.log
```

Evidence paths must resolve below `test_log/`. Unknown evidence classes, missing markers, paths outside `test_log/`, and missing executables fail with non-zero status.

## NRF schema maintainer validation

These are NRF maintainer gates. They do not enable `trusted_af_sbi`:

```bash
NRF_SOURCE_DIR=/home/tonywang/OAI/oai-cn5g-nrf \
  redcap_library/bash_tool/scripts/aiot_registered_check.sh build-nrf-candidate

NRF_CONFORMANCE_TARGET=deployed \
  NRF_CANDIDATE_IMAGE=oai-nrf@sha256:59bbe00f83453e4543eb8c37a77db024711f3cd74708a3819ac6b407b60e901f \
  redcap_library/bash_tool/scripts/aiot_registered_check.sh nrf-aiotf-conformance
```

The build and conformance commands map to registry entries `build_aiotf_nrf_candidate` and `validate_aiotf_nrf_candidate`. Conformance uses unique profiles and covers create/read/update/delete, invalid/unknown input, repeated/concurrent PUT, target/area discovery, AMF regression, and trap-based cleanup. Update `task_log/tasks.json` before the long build.

## AIOTF NRF client validation

```bash
redcap_library/bash_tool/scripts/aiot_registered_check.sh aiotf-nrf-client
```

This command maps to registry entry `validate_aiotf_nrf_client`. It uses a fixed test instance to validate create, read-back, area discovery, HTTP rejection, timeout, duplicate/restart update, deregistration, and NRF unavailable. A trap removes its test containers and profile. The PASS marker is:

```text
AIOTF_NRF_CLIENT PASS accepted=1 rejection=1 timeout=1 duplicate=1 restart=1 deregistration=1 unavailable=1 cleanup=empty
```

This PASS satisfies only `nrf_aiotf_profile_registered_and_read_back`. After the Naiotf listener is bound, `AIOTF_SERVICE_READY ready=0 reason=amf_dependency_unavailable` is the expected fail-closed result and must not be interpreted as complete `trusted_af_sbi` readiness.

## Naiotf Inventory validation

```bash
redcap_library/bash_tool/scripts/aiot_registered_check.sh aiotf-naiotf-inventory
```

This command maps to registry entry `validate_aiotf_naiotf_inventory`. It starts a bounded AIOTF service, h2c callback proxy, and callback backend on `public_net`, then validates 0/1/60/61 Tags, duplicate Tags, a wrong AF, timeout notification, callback 204, unique restart `transId`, and cleanup. The PASS marker is:

```text
AIOTF_NAIOTF_RUNTIME PASS protocol=h2c tags=0,1,60,61 auth=rejected callback=204 restart=unique cleanup=empty
```

Retained evidence is in `test_log/compiler_logs/aiotf_naiotf_inventory_runtime_2026-07-20_16-35-47.log`. This gate completes only the bounded `Naiotf_AIoT_Inventory` surface. The AMF/NGAP/RRC round trip is still missing, so complete `trusted_af_sbi` readiness remains fail closed.

## AMF and standard-path status

| Probe | Current result | Operator decision |
|---|---|---|
| AIOTF NRF register/read-back/discovery | PASS | Proves only that NRF accepts the AIOTF NF profile |
| `POST /namf-aiot/v1/transfer` to OAI AMF `89e15886` | HTTP 404; no route, model, or handler | AIOTF and AMF do not have working communication |
| Topology-2 NGAP/RRC UE Reader endpoint | No repository owner or marker | Stop the standard-path gate `[Needs Verification]` |
| OAI NEF `358f2131` `Nnef_AIoT_*` | No route, model, authorization, or callback owner | Do not enable `third_party_af_nef` `[Needs Verification]` |

Sharing `public_net` proves only IP reachability. It does not prove that a `Namf_AIoT` service exists. Do not substitute NRF PASS, N6 UDP, or Compose health for AMF round-trip evidence.

## Failure handling

| Marker or error | Action |
|---|---|
| `AIOT_OPERATOR_REJECT reason=unsupported_profile` | Select `experimental_n6`; do not silently downgrade a requested standard profile |
| `AIOTF_CONFIG_REJECT` | Fix Tags, pending context, timeout, address, or port before restart |
| `Address already in use` | Inspect both Docker static addresses and host UDP 36900; do not stop unrelated services |
| `AIOTF_DIAGNOSTIC_REJECT reason=no_pending_context` | Match Tag, frame, and slot to one active pending context |
| `AIOTF_NRF_GATE REJECT` | Use `reason=http_rejected|timeout|unavailable` to fix the NRF URI, schema, or connection; do not alias another NF type |
| AMF `/namf-aiot/v1/transfer` returns 404 | Retain the probe and AMF commit; wait for or implement the real route/model/handler, and do not call another AMF API instead |
| AMF/RAN or NEF gate unavailable | Stop the evidence ladder; NRF/Naiotf PASS does not replace a missing endpoint |

Always finish with `./mmtc.menu.bash aiot down`. Do not delete CN5G volumes.
