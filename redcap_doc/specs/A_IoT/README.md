# Ambient IoT (A-IoT) References

## Purpose

- Keep local 3GPP references for Ambient IoT design and review.
- This directory is reference material. The local profile below is experimental and does not indicate standards-compliant OAI Ambient IoT support.

## Confirmed Experiment Boundary

| Item | Decision |
|---|---|
| Connectivity | Topology 2: gNB controls a RedCap UE acting as a UE Reader over NR Uu. |
| CW source | gNB or an independent CW node provides a continuous tag-directed CW beam. The UE does not provide continuous CW. |
| Beam roles | Beam A carries NR Uu between gNB and UE. Beam B provides CW to the tag. |
| R2D | The UE Reader wakes briefly to send R2D paging or command. |
| D2R | The tag backscatters to the UE Reader. The implemented Manchester encoding is an experimental profile, not current TS 38.291 D2R behaviour. |
| First scope | One tag, short Inventory Report, and deterministic validation. |
| Report transport | Experimental fixed-size UDP report over the UE PDU-session TUN, NR Uu, gNB, and UPF to an AIOTF-side endpoint. It does not overload RRC or NAS. |

## Implemented Experimental Profile

| Layer | Owner | Disabled-by-default implementation |
|---|---|---|
| RFsim relay | `radio/rfsimulator/simulator.cpp` | `aiot_t2` routes CW/R2D/D2R control packets without changing the normal IQ path. |
| Tag/CW node | `radio/rfsimulator/stored_node.c` | Existing `replay_node` supports deterministic tag, CW, reader, and self-test modes. |
| UE codec | `openair1/PHY/NR_UE_TRANSPORT/nr_ue_rf_helpers.c` | Encodes R2D and validates D2R length, Manchester pairs, and CRC. |
| UE role gate | `executables/nr-ue.c` | Gates operations on connection, C-DRX active state, and the configured slot window. |
| UE report | `executables/nr-ue.c` | Sends one 40-byte UDP report through `oaitun_ue<N>` to an AIOTF-side endpoint. |
| AIOTF state | `openair3/AIOTF/aiotf_inventory.c` | Owns correlation, binding, selection, serialization, arbitration, timeout, evidence, and pre-R2D failover state. |
| AIOTF process | `openair3/AIOTF/aiotf_service.c` | Runs the fail-closed `experimental_n6` listener, validates pending context, and emits profile-scoped lifecycle/result markers. |

Enable the RFsim path explicitly with `--rfsimulator.options aiot_t2`. Select exactly one UE role:

| Role option | R2D | D2R | Report |
|---|---:|---:|---:|
| `--aiot-t2-reader` | yes | yes | yes |
| `--aiot-t2-observer` | no | yes | yes |

The two role options are mutually exclusive. Both require Tag ID, slot-window, stable reader handle, report IPv4 address, and report port.

## AIOTF Binding and Scheduling

| Tag range | Eligible readers | Default primary | Diversity observer |
|---|---|---|---|
| 1-20 | UE1 | UE1 | none |
| 21-30 | UE1, UE2 | UE1 | UE2 |
| 31-40 | UE1, UE2 | UE2 | UE1 |
| 41-60 | UE2 | UE2 | none |

- The Tag stores no reader list.
- Normal mode activates only the primary reader.
- Diversity mode is restricted to Tags 21-40. One primary sends R2D; the other UE is D2R-only.
- AIOTF sorts selected Tag IDs and assigns one distinct response slot and session ID per Tag.
- The first correlation-, session-, Tag-, epoch-, reader-, deadline-, and CRC-valid report wins.
- Later identical reports are duplicate evidence. Different valid payloads are conflict evidence.
- AIOTF performs no MRC, soft combining, or IQ combining.
- Shared-tag failover is permitted only before R2D. It changes the primary and increments `binding_epoch`.

## Single-Tag RFsim Procedure

Build the existing simulated-node target:

```bash
cmake --build --preset default --target replay_node
```

Start one UE Reader with the profile enabled on gNB and UE. The slot window below is an evidence window, not a power-consumption profile:

```bash
MMTC_ACTIVE_UES=1 \
MMTC_TOTAL_UES=56 \
MMTC_GNB_EXTRA_OPTIONS="--rfsimulator.options aiot_t2" \
MMTC_UE_EXTRA_OPTIONS="--rfsimulator.options aiot_t2 \
  --aiot-t2-reader --aiot-t2-tag-id 25 \
  --aiot-t2-window-period 80 --aiot-t2-window-offset 0 \
  --aiot-t2-window-duration 80 --aiot-t2-reader-handle 1 \
  --aiot-t2-report-ip 192.168.72.135 --aiot-t2-report-port 36900" \
redcap_interface/bash_library/fc_mmtc_smoke_validation.sh
```

Capture the report at the current Compose ext-DN:

```bash
docker exec oai-ext-dn timeout 60 \
  tcpdump -i any -nn -XX -c 1 udp port 36900
```

In another shell, start Tag 25 before the bounded CW source:

```bash
cmake_targets/ran_build/build/radio/rfsimulator/replay_node \
  --aiot-tag-rfsim 192.168.70.140 4043 25 01020304 &
tag_pid=$!
sleep 0.1
cmake_targets/ran_build/build/radio/rfsimulator/replay_node \
  --aiot-cw-rfsim 192.168.70.140 4043 576 1
wait "$tag_pid"
```

| Owner | Success markers | Failure markers |
|---|---|---|
| Tag/CW | `AIOT_T2_TAG_REGISTER_SENT`, `AIOT_T2_CW_CAPTURE`, `AIOT_T2_BACKSCATTER` | `AIOT_T2_CW_REJECT`, `AIOT_T2_LINECODE_REJECT`, `AIOT_T2_CRC_REJECT` |
| gNB RFsim | `AIOT_T2_R2D_RELAY`, `AIOT_T2_D2R_RELAY` | relay marker with zero destinations |
| UE Reader | `AIOT_T2_R2D_SENT`, `AIOT_T2_D2R_CRC_OK`, `AIOT_T2_UE_REPORT_SENT` | `AIOT_T2_R2D_REJECT`, `AIOT_T2_D2R_REJECT`, `AIOT_T2_UE_REPORT_REJECT` |
| AIOTF test | `AIOTF_SERIALIZED_60_TAGS`, `AIOTF_INVENTORY_TEST PASS` | non-zero test exit or missing marker |

Disable the experiment by recreating the services without `MMTC_GNB_EXTRA_OPTIONS` and `MMTC_UE_EXTRA_OPTIONS`. Normal NR/RFsim requires no A-IoT option.

## Evidence and Claim Boundary

| Evidence | Result | Scope |
|---|---|---|
| `test_log/build_logs/build_aiot_t2_cross_feature_boundaries_2026-07-19_23-12-54.log` | focused codec, Tag, AIOTF, and affected-target build PASS | source and deterministic executable evidence |
| `test_log/compiler_logs/aiot_t2_final_image_e2e_report_2026-07-19_22-50-15.log` | one UE report traversed TUN/Uu/gNB/UPF to ext-DN | single-reader RFsim evidence |
| `test_log/compiler_logs/aiot_t2_two_ue_reader_observer_runtime_2026-07-19_23-32-03.log` | one R2D sender, two CRC-valid reports, two 40-byte UDP packets | Tag 25 diversity RFsim evidence |
| `test_log/compiler_logs/aiotf_serialized_60_tag_runtime_2026-07-19_23-40-13.log` | 60 ordered transactions, slots 1000-1059, 30/30 primary load | AIOTF scheduler executable evidence; not 60 simultaneous RF tags |
| `test_log/compiler_logs/aiotf_registered_t2_demo_ip_fix_2026-07-20_13-36-00.log` | AIOTF live/ready, first-valid, duplicate evidence, wrong-slot rejection, idempotent cleanup | `experimental_n6` diagnostic listener evidence; not NRF/SBI/AMF/NEF evidence |
| `test_log/compiler_logs/aiotf_naiotf_inventory_runtime_2026-07-20_16-35-47.log` | h2c 0/1/60/61, duplicate, 403, timeout callback 204, restart uniqueness, NRF dependency, cleanup | Bounded `Naiotf_AIoT_Inventory` evidence; not AMF/NGAP/RRC round-trip evidence |
| `test_log/compiler_logs/aiotf_nrf_client_after_naiotf_2026-07-20_16-41-54.log` | NRF seven-boundary regression PASS after Naiotf change | NRF dependency regression evidence |

Known limits:

- The 40-byte UE wire report contains magic, version, payload length, flags, reader handle, Tag ID, frame, slot, and a 16-byte payload. It does not carry `correlation_id`, `session_id`, or `binding_epoch`; the `experimental_n6` listener supplies these only from one explicit Tag/frame/slot pending context. Ambiguous context is rejected before arbitration.
- The configurable experimental timeout, default 60000 ms in Compose, is not a 3GPP timer. Its coincidence with an NR paging occasion has no implemented shared owner and remains `[Needs Verification]`.
- RFsim evidence proves deterministic logical CW/backscatter routing. It does not prove calibrated RF power, leakage tolerance, physical dual-beam isolation, or 3GPP conformance.
- Diversity evidence retains independent reports only. It does not combine samples or soft information.
- Bounded Naiotf uses a local trusted-AF allow-list and a project-specific permanent-ID mapping. It does not prove OAuth, HTTPS callback, `targetArea`, Command, ADM, security, or complete SBI readiness `[Needs Verification]`.

## Current CN5G Boundary

| Interface | Evidence | Status |
|---|---|---|
| AIOTF to NRF | Native AIOTF profile lifecycle, read-back, area discovery, and cleanup markers | Implemented over HTTP/2 |
| Trusted AF to AIOTF | Bounded h2c Inventory request and HTTP/2 notification | Implemented experimental surface; not complete SBI conformance |
| AIOTF to AMF | OAI AMF `89e15886` returns HTTP 404 for `POST /namf-aiot/v1/transfer`; no route/model/handler owner | Missing `[Needs Verification]` |
| AMF/gNB to UE Reader | No matching topology-2 NGAP/RRC endpoint in the selected source and Stage-3 baseline | Missing `[Needs Verification]` |
| AF to NEF | OAI NEF `358f2131` has no `Nnef_AIoT_*` route/model/auth/callback owner | Missing `[Needs Verification]` |

NRF registration proves NF discovery only. AIOTF and AMF do not currently have a working A-IoT protocol channel. N6 UDP remains a diagnostic report path and must not be presented as an AMF, NGAP/RRC, or NEF replacement.

## Reading Route

| Need | Start with |
|---|---|
| Two-week RedCap-to-AIOTF implementation and function course for GPT 5.6 Luna | `../../manuals/aiot_redcap_to_aiotf_two_week_course.zh-TW.md` |
| Implemented architecture and claim boundaries | `../../manuals/aiot_tag_aiotf_architecture.zh-TW.md` or `.en.md` |
| Operator commands, skill, markers, and cleanup | `../../manuals/aiot_tag_aiotf_operator.zh-TW.md` or `.en.md` |
| Function-level trace | `../function_reference/aiot_tag_aiotf_function_trace.md` |
| Retained validation summary | `../../../redcap_library/library_reports_summary/aiotf_cn5g_experimental_n6_validation_report.md` |
| Service requirements and study background | `TR22369.pdf`, `TR22840.pdf` |
| Architecture and AIOTF | `TR23700.pdf`, `TS23369.pdf`, `TS24369.pdf`, `TS29369.pdf`, `TS33369.pdf` |
| Topology 2 and RAN study | `TR38769.pdf`, `TR38848.pdf` |
| PHY, MAC, and RF | `TS38291_PHY.pdf`, `TS38391_MAC.pdf`, `TS_138_191(Transmission&reception).pdf`, `TS_138_194(CW_BS).pdf` |

## Terms

| Term | Meaning in this experiment |
|---|---|
| CW2D | Continuous carrier wave from gNB/CW node to the tag for energy and a reflection reference. |
| R2D | Reader-to-device control signal from UE Reader to tag. |
| D2R | Device-to-reader tag backscatter received by UE Reader. |
| A-IoT radio | The tag-to-reader radio interface containing R2D and D2R; it is distinct from NR Uu. |

## Rule

- Check exact wording against the source PDF before making a 3GPP compliance claim.
- Mark the experimental D2R Manchester profile and any bistatic-CW conclusion as `[Needs Verification]` until PHY validation succeeds.
