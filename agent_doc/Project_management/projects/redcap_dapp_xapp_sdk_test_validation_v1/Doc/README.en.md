# RedCap dApp/xApp SDK Test Validation

## Scope

- This page explains how to test the RedCap dApp/xApp SDK slice.
- Primary references are under `dev_refer/`.
- Static checks do not claim 64 UE / staged 5 MHz-to-20 MHz BWP runtime PASS.

## SDK routes

| Need | File |
|---|---|
| Scenario, API behavior, developer notes, and current evidence | [README.en.md](./README.en.md) |
| SDK development workflow | [sdk_development_guide.en.md](./sdk_development_guide.en.md) |
| 56 UE Gate E-Core manual reproduction | [gate_e_core56_manual_reproduction.en.md](./gate_e_core56_manual_reproduction.en.md) |
| Final Gate E-Core accepted report | [gate_e_core56_ab_latency_2026-07-09.md](../report/gate_e_core56_ab_latency_2026-07-09.md) |

## API / config behavior

| API | Language | Purpose | Current evidence |
|---|---|---|---|
| `redcap_xapp_make_priority_hint` | C | Build one UE priority hint from UL buffer and weights | syntax check target |
| `redcap_xapp_select_top_priority_hint` | C | Select the highest-priority UE; ties use lower RNTI | syntax check target |
| `make_priority_hint` | Python | Python equivalent of the C priority hint builder | self-test |
| `select_top_priority_hint` | Python | Python equivalent of top-UE selection | self-test |
| `redcap_dapp_guard_prb_allocation` | C | Validate a 5 MHz BWP profile, I/Q presence, and PUCCH/PUSCH ratio intent | syntax check target |
| `redcap_dapp_guard_prb_allocation` | Python | Python equivalent of the dApp allocation guard | self-test |
| `redcap_dapp_access_pressure_policy` | C | Convert RA/PUCCH collision proxy counters into bounded PUCCH/PUSCH ratio intent, then call the dApp allocation guard | syntax check target |
| `redcap_dapp_access_pressure_policy` | Python | Python equivalent of the access-pressure policy | self-test |

Key fields:

- [RNTI]: UE identifier; must be non-zero.
- [priority_weight]: xApp output used by dApp metadata.
- [bwp_prbs]: runtime-derived BWP PRB marker; for the 5 MHz / 30 kHz SCS profile, local notes expect about `12` PRBs `[Needs Verification]`.
- [pucch_ratio_permille] / [pusch_ratio_permille]: ratio in permille; sum must be at most `1000`.
- [has_iq_samples]: dApp requires I/Q observation evidence before apply.

## Access-pressure policy

- [Purpose]: mitigate access pressure for the first 32 UE on 5 MHz BWP before xApp-guided expansion to 20 MHz for the later UE group.
- [Inputs]: RA retry count, Msg3 failure count, PUCCH resource reject count, CRC/discard count, previous pressure EWMA, BWP PRB marker, priority weight, and I/Q availability.
- [Pressure score]: `50 * ra_retry + 120 * msg3_failure + 160 * pucch_resource_reject + 40 * crc_discard`, clamped to `1000`.
- [EWMA]: `0.7 * previous + 0.3 * current`, implemented as integer arithmetic.
- [Ratio mapping]:
  - low pressure: PUCCH `200`, PUSCH `600`.
  - medium pressure: PUCCH `300`, PUSCH `500`.
  - high pressure: PUCCH `400`, PUSCH `400`.
- [Guard boundary]: the policy result is applied only if `redcap_dapp_guard_prb_allocation` returns ACK.
- [Current evidence]: Python SDK self-check, dApp/xApp contract self-test, C syntax check, Gate D marker runtime, and Gate E-Core 56 UE A/B Launch-to-TUN comparison pass.

## Command usage

Run static validation:

```bash
python3 agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/check_dapp_xapp_sdk_test_validation.py
```

Run SDK contract validation:

```bash
python3 agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/dapp_xapp_sdk_contract_selftest.py
```

Run OpenSpec validation:

```bash
openspec validate redcap-dapp-xapp-sdk-test-validation --strict
```

Run Gate C E3 loopback dependency/runtime check:

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py
```

Gate C returns `blocked` when `dev_refer/dapp_dev_need/libe3` has no existing loopback binary or required local build dependencies are absent.

Capture Gate C configure evidence:

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py --try-configure
```

Current configure evidence is saved at `test_log/compiler_logs/gate_c_libe3_configure_2026-07-05_18-43-41.log`; the current blocker is missing offline `tl::expected` target/cache, not `asn1c`.

If network FetchContent is allowed, use a clean build directory:

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py --try-configure --allow-fetch --build-dir dev_refer/dapp_dev_need/libe3/build/redcap-gate-c-fetch
```

Current fetch evidence is saved at `test_log/compiler_logs/gate_c_libe3_configure_fetch_2026-07-05_18-46-35.log`; sandbox DNS could not resolve `github.com`, and escalation was rejected because workspace credits are unavailable.

Run Gate C with the project-local expected shim:

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py --try-configure --use-local-expected-stub --try-build --build-dir dev_refer/dapp_dev_need/libe3/build/redcap-gate-c-local-expected
```

Current Gate C runtime evidence:

- POSIX IPC/TCP loopback PASS: `test_log/compiler_logs/gate_c_libe3_runtime_test_role_pair_posix_2026-07-06_11-58-08.log`
- Full-loop latency PASS: `test_log/compiler_logs/gate_c_libe3_runtime_test_bench_full_loop_latency_2026-07-06_11-58-23.log`
- Total round-trip latency: p99 `183 us`, max `260 us`

Run Gate D source readiness check:

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_d_rfsim_marker_check.py
```

Run Gate D RFsim marker scan after starting gNB with the marker environment enabled:

```bash
cd ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap
REGISTRY= \
TAG=latest \
GNB_IMG=oai-gnb \
NRUE_IMG=oai-nr-ue \
GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml \
MMTC_N_RB_DL=106 \
OAI_REDCAP_DAPP_GATE_D_MARKER=1 \
MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0" \
docker compose -f docker-compose.yml -f docker-compose.mmtc.yml up -d --force-recreate oai-gnb oai-nr-ue2
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_d_rfsim_marker_check.py --gnb-log <gNB-log-path> --ue-log <UE-log-path> --require-runtime --require-bwp-mhz 5
```

Gate D source readiness plus `nr-softmodem` build evidence is saved at `test_log/build_logs/build_nr-softmodem_2026-07-06_gate-d-pucch-marker.log`. It proves that the gNB ULSCH/PUSCH/PDCCH path calls the dApp PRB guard after `config_uldci()`, that the PUCCH FAPI path calls the same guard after `nr_configure_pucch()`, and that the target still builds.

Current Gate D 5 MHz RFsim evidence:

- gNB log: `test_log/runtime_logs/gate_d_5mhz_gnb_2026-07-06_17-16-57.log`
- UE2 log: `test_log/runtime_logs/gate_d_5mhz_ue2_2026-07-06_17-16-57.log`
- gNB observed `[RedCap RA][gNB Msg2 BWP selected]` with `dl_bwp_size 12` and `ul_bwp_size 12`.
- UE2 observed `SIB1 RedCap initial BWP decision` and applied DL/UL BWP size `12`.
- The old logs also show a RedCap RA DCI bit-length mismatch: gNB `dci_bits 35`, UE `dci_bits 39`.
- The source fix aligns both sides to the current 12 PRB DL BWP for RedCap Case B RA common DCI sizing.
- Local rebuilt image evidence: `test_log/build_logs/rebuild_local_oai_images_2026-07-07_00-35-33_dapp_access_pressure_policy.log`.
- Post-rebuild failure evidence with CSI-RS/SRS enabled: `test_log/runtime_logs/gate_d_access_pressure_gnb_2026-07-07_00-45_local.log`.
- Failure cause: gNB reached RA/RAR/Msg3, then asserted in `encode_cellGroupConfig()` on `nzp-CSI-RS-ResourceToAddModList`.
- Gate D PASS gNB log: `test_log/runtime_logs/gate_d_access_pressure_gnb_2026-07-07_00-47_local_no_csirs_srs.log`.
- Gate D PASS UE2 log: `test_log/runtime_logs/gate_d_access_pressure_ue2_2026-07-07_00-47_local_no_csirs_srs.log`.
- The PASS run used local images and `MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0"`.
- gNB confirms `CSI-RS 0, SRS 0`, 12 PRB RedCap RA DCI, `[RedCap dApp Gate D][gNB MAC PUCCH]`, and `[RedCap dApp Gate D][gNB MAC UL]` with marker `"RedCap dApp PRB decision"`.
- Gate D checker PASS: `gate_d_rfsim_marker_check.py --require-runtime --require-bwp-mhz 5`.
- Do not claim 64 UE runtime PASS or access-pressure mitigation effectiveness from this Gate D run.

Prepare Gate E 64 UE preflight:

```bash
bash ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh 64
bash redcap_interface/generate_mmtc_cn_db_overlay.sh 64
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_e_64ue_stage_check.py
```

Current Gate E preflight evidence:

- RFsim overlay: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml` now exposes UE1..UE64.
- RFsim base compose: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml`.
- CN/AMF source: `redcap_interface/redcap_mmtc_smoke_validation.sh` defaults `CN_COMPOSE` to `/home/tonywang/OAI/oai-cn5g/docker-compose.yaml`, whose service list includes `oai-amf`, `mysql`, `oai-smf`, and `oai-upf`.
- CN DB overlay: `test_log/runtime_configs/oai_db_mmtc_64.sql` and `test_log/runtime_configs/oai-cn5g_mmtc_64.override.yml`.
- Config merge evidence: `docker compose -f /home/tonywang/OAI/oai-cn5g/docker-compose.yaml -f test_log/runtime_configs/oai-cn5g_mmtc_64.override.yml config --services` lists `oai-amf`; `docker compose -f docker-compose.yml -f docker-compose.mmtc.yml config --services` under the RFsim RedCap directory lists 64 `oai-nr-ue*` services.
- First-stage profile: `gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml` keeps the RF carrier at 106 PRBs and sets the RedCap active/initial BWP to 12 PRBs.
- Later-stage proxy profile: `gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml` provides a 51 PRB 20 MHz proxy `[Needs Verification]`.
- Checker result: `gate_e_64ue_stage_check.py` reports `[PASS] Gate E static preflight is ready for 64 UE staged RFsim`.
- Runtime evidence checker shape:

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_e_64ue_stage_check.py \
  --stage first32 \
  --gnb-log test_log/compiler_logs/mmtc_smoke_<timestamp>_gnb.log \
  --summary-log test_log/compiler_logs/mmtc_stage_scan_<timestamp>_summary.log
```

Gate E first32 runtime attempt on 2026-07-07:

- Summary log: `test_log/compiler_logs/mmtc_stage_scan_2026-07-07_11-11-52_summary.log`.
- gNB log: `test_log/compiler_logs/mmtc_smoke_2026-07-07_11-11-52_gnb.log`.
- Result: `sample=32 running=32 attach=0 pdu=0 tun=0 gnb_restart=0 failures=32`.
- Positive evidence: the rebuilt gNB did not restart and the log contains `260` `[RedCap dApp Gate E][PUCCH pressure]` markers.
- Negative evidence: no `Assertion`, `assert`, `Not enough resources`, `event_asio_agent`, `Aborted`, or `Segmentation` marker appears in the gNB log.
- xApp/RIC evidence: `mmtc_smoke_2026-07-07_11-11-52_xapp-rc-moni.log` and `..._nearrt-ric.log` contain E42 setup, two RC subscriptions, and four RC Indications.
- Control boundary: no RIC Control request/ACK marker was observed in the xApp or nearRT-RIC Docker logs.
- Current blocker: the 12 PRB BWP run repeats Msg4/RRC Setup failures and does not reach UE registration/PDU session.
- Gate E runtime PASS is still pending; no 64 UE attach/control/collision-load evidence has been produced yet.

Gate E first32 DL TDA fix attempt on 2026-07-07:

- Build log: `test_log/build_logs/build_nr-softmodem_2026-07-07_11-38-37_gate-e-redcap-tda.log`.
- Local image rebuild log: `test_log/build_logs/rebuild_local_oai_images_2026-07-07_11-39-43_gate-e-redcap-tda.log`.
- Summary log: `test_log/compiler_logs/mmtc_stage_scan_2026-07-07_12-14-11_summary.log`.
- gNB log: `test_log/compiler_logs/mmtc_smoke_2026-07-07_12-14-11_gnb.log`.
- Result: `sample=32 running=32 attach=0 pdu=0 tun=0 gnb_restart=0 failures=32`.
- Positive evidence: `nr_radio_config.c` rebuilds the RedCap initial DL BWP PDSCH TDA list for the 12 PRB BWP, and the gNB log contains `2` `[RedCap RA][gNB DL TDA]` markers with `first_start_symbol 2`.
- Positive evidence: the old `Msg4 vrb_map fail` marker is no longer present; the gNB log shows `32` Msg4 ACK markers and `32` `Send RRC Setup` markers.
- Remaining failure evidence: the gNB log still has `85` `[RedCap RA][gNB Msg4 compact fallback]` markers and `1` `[RedCap RA][gNB Msg2 vrb_map fail]` marker.
- UE-side evidence: each UE1..UE32 Docker log contains `Generating RRCSetupComplete` once.
- Core-network boundary: the gNB/AMF logs do not show UE registration or PDU-session progress, and stage summary still reports no TUN interface.
- xApp/RIC boundary: the stage script did not persist 12:14 xApp/RIC log files; live Docker logs show E42 setup, two RC subscriptions, and RC Indications, but no RIC Control request/ACK marker.
- Gate E runtime PASS is still pending; the next blocker is SRB1/UL-DCCH or post-RRCSetupComplete handling on the 12 PRB BWP.

Gate E first32 connected DCI BWP runtime rerun on 2026-07-07:

- Root cause narrowed from log evidence: after Msg4 ACK, gNB connected common-search-space UL DCI used the regular 51 PRB initial UL BWP RIV width while the UE had applied the 12 PRB RedCap SIB1 initial UL BWP.
- Failure signature: gNB logged `dci_freq 204` for a 5 PRB grant, which is the 51 PRB RIV value; UE then decoded the shifted low bits as `TDA index from DCI 12` and could not deliver SRB1/UL-DCCH cleanly.
- Source fix: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c` now preserves RedCap initial DL/UL BWP start/size for connected DCI through `apply_redcap_initial_bwp_if_needed()`.
- Source build evidence: `test_log/build_logs/build_nr-softmodem_2026-07-07_12-42-09_gate-e-redcap-dci-bwp_retry.log`.
- Docker image rebuild evidence: `test_log/build_logs/rebuild_local_oai_images_2026-07-07_23-05-19_gate-e-redcap-dci-bwp_retry2_escalated.log`.
- Summary log: `test_log/compiler_logs/mmtc_stage_scan_2026-07-07_23-18-49_summary.log`.
- gNB log: `test_log/compiler_logs/mmtc_smoke_2026-07-07_23-18-49_gnb.log`.
- xApp/RIC Docker logs: `test_log/compiler_logs/mmtc_smoke_2026-07-07_23-18-49_xapp-rc-moni.log` and `test_log/compiler_logs/mmtc_smoke_2026-07-07_23-18-49_nearRT-RIC.log`.
- Result: `sample=32 running=32 attach=32 pdu=32 tun=32 forward_ping_ok=32 gnb_restart=0 failures=0`.
- Runtime marker evidence: the gNB log contains `128` `[RedCap RA][gNB DCI BWP]` markers, `32` `Received RRCSetupComplete`, `32` `Received RRCReconfigurationComplete`, and `32` `PDU Session Setup: ID=10` markers.
- dApp evidence: the gNB log contains `34291` `[RedCap dApp Gate D][gNB MAC UL]` apply markers and `28` `[RedCap dApp Gate E][PUCCH pressure]` markers on the 12 PRB BWP.
- Retry boundary: the gNB log still contains `1` transient `[RedCap RA][gNB Msg4 vrb_map fail]` and `90` compact-fallback markers, but no `RA Procedure failed at Msg4`; the final stage summary reports zero failures.
- UE-side fix evidence: UE1..UE32 each generated `RRCSetupComplete`; no UE Docker log contains `TDA index from DCI 12`.
- xApp/RIC evidence: xApp Docker log shows E42 setup, two RC subscriptions, `5` RC Indication messages, `RRC Setup Complete`, `RRC connected`, subscription delete, and `Test xApp run SUCCESSFULLY`; nearRT-RIC Docker log shows E2 setup and RAN function 3 `ORAN-E2SM-RC`.
- Control boundary: no RIC Control request/ACK marker was observed in the xApp or nearRT-RIC Docker logs.
- Gate E first32 checker PASS: `gate_e_64ue_stage_check.py --stage first32 --gnb-log test_log/compiler_logs/mmtc_smoke_2026-07-07_23-18-49_gnb.log --summary-log test_log/compiler_logs/mmtc_stage_scan_2026-07-07_23-18-49_summary.log`.
- Gate E runtime PASS is still pending for the full 64 UE / 20 MHz proxy stage and collision-load access-pressure effectiveness; this first32 result only proves the 32 UE 5 MHz stage.

Gate E-Core 56 UE A/B runtime on 2026-07-09:

- Gate E is now two-tiered: Gate E-Core is the SDK v1 engineering gate; Gate E-Stretch keeps strict 64 UE stress evidence non-blocking.
- Baseline summary: `test_log/compiler_logs/mmtc_stage_scan_2026-07-09_10-27-10_summary.log`.
- dApp summary: `test_log/compiler_logs/mmtc_stage_scan_2026-07-09_10-42-43_summary.log`.
- Baseline latency CSV: `test_log/compiler_logs/mmtc_smoke_2026-07-09_10-27-10_access_latency.csv`.
- dApp latency CSV: `test_log/compiler_logs/mmtc_smoke_2026-07-09_10-42-43_access_latency.csv`.
- dApp gNB marker log: `test_log/compiler_logs/mmtc_smoke_2026-07-09_10-42-43_gnb.log`.
- Result: both runs reached `sample=56 running=56 attach=56 pdu=56 tun=56 forward_ping_ok=56 gnb_restart=0 failures=0`.
- Launch-to-TUN comparison: baseline median/p95/max `436318/703145/722926 ms`; dApp median/p95/max `441487/708146/728189 ms`.
- Boundary: this is a valid A/B comparison, not a dApp latency-improvement claim.
- Gate E-Core checker PASS: `gate_e_64ue_stage_check.py --stage core56-ab`.
- Report: `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/report/gate_e_core56_ab_latency_2026-07-09.md`.

## Step-by-step recap

1. Confirm local `dev_refer/` references exist.
2. Confirm xApp priority hint APIs exist in C and Python.
3. Confirm dApp PRB allocation APIs exist in C and Python.
4. Confirm SWIG definition files exist for `libe3` and I/Q saver.
5. Run the SDK contract self-test.
6. Run the Gate C E3 loopback checker.
7. Run the Gate D source readiness checker.
8. Run the Gate E preflight checker.
9. For runtime, run `redcap_interface/redcap_mmtc_stage_scan.sh`, then validate both `mmtc_smoke_<timestamp>_gnb.log` and `mmtc_stage_scan_<timestamp>_summary.log`.
10. Treat Gate E-Core as closed by the 56 UE A/B run; keep Gate E-Stretch pending until strict 64 UE upper-bound evidence is needed.

## Example logic

- xApp receives UE metrics.
- xApp computes priority hints.
- dApp receives the selected hint.
- dApp checks I/Q observation availability.
- dApp computes access pressure from the RA/PUCCH collision proxy.
- dApp validates the 5 MHz BWP profile and PUCCH/PUSCH ratios.
- dApp emits an apply/reject result.

## Visualization

- Use `dev_refer/dapp_dev_need/dApp-library/examples/spectrum_dapp.py` as the reference for visualization mode.
- Relevant options from that reference include:
  - `--demo-gui`
  - `--iq-plotter-gui`
  - `--energy-gui`
  - `--num-prbs <derived 5 MHz PRB count>`
- Visualization is not a PASS gate until the dApp runtime path is connected.

## Expected markers

- `RedCap xApp priority hint`
- `RedCap dApp PRB decision`
- `RedCap dApp access pressure policy`
- `[RedCap dApp Gate E][PUCCH pressure]`
- `[RedCap RA][gNB DL TDA]`
- `[RedCap dApp Gate D][gNB MAC UL] gNB-side apply marker`
- `[RedCap dApp Gate D][gNB MAC PUCCH] gNB-side PUCCH marker`
- Gate C source path: `dev_refer/dapp_dev_need/libe3/tests/integration/test_role_pair_posix.cpp`
- Gate D source path: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c`
- Gate D PUCCH source path: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_uci.c`
- Gate D 5 MHz BWP profile: `ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml`
- Gate D runtime env passthrough: `OAI_REDCAP_DAPP_GATE_D_MARKER` in `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml`
- Gate E preflight checker: `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_e_64ue_stage_check.py`
- Gate E runtime summary: `test_log/compiler_logs/mmtc_stage_scan_<timestamp>_summary.log`
- Gate E 64 UE overlay: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml`
- Gate E CN DB overlay: `test_log/runtime_configs/oai_db_mmtc_64.sql`
- Gate D I/Q reference: `dev_refer/dapp_dev_need/E3Controller/src/e3sm/iq_pipeline.h` and `slot_iq_pipeline.h`
- PDCCH command path: `config_uldci()` followed by `fill_dci_pdu_rel15()` in the ULSCH path `[Needs Verification: TS 38.212 Section 7.3.1.1 / TS 38.214 Section 6.1]`

## Limitations

- Gate B currently verifies SWIG definitions, not generated SWIG module runtime.
- Gate C E3 loopback passed with the project-local `tl_expected` test shim.
- Official `tl_expected` FetchContent remains unavailable; do not use the local shim as production dependency evidence.
- Gate D source hook readiness, `nr-softmodem` build PASS, and small RFsim marker validation PASS are present.
- The DCI bit-length source fix builds for both `nr-softmodem` and `nr-uesoftmodem`.
- Gate D runtime env passthrough is present in the compose overlay, and the 5 MHz BWP profile was mounted in the gNB container for the latest run.
- The 5 MHz profile keeps the RF carrier at 106 PRBs while BWP1 and RedCap DL/UL initial BWP are 12 PRBs at 30 kHz SCS `[Needs Verification]`; runtime logs confirm RA/SIB1 uses size `12`.
- Gate D PASS currently depends on disabling CSI-RS/SRS through CLI override; CSI-RS/SRS enabled RFsim remains a blocker before production-style Gate E claims.
- Gate D currently covers the ULSCH/PUSCH/PDCCH and PUCCH marker paths. The dApp access-pressure policy is implemented and unit-tested, but runtime effectiveness under collision load is still pending.
- Gate E static preflight is ready, the first32 post-DCI-BWP runtime reaches `attach=32`, `pdu=32`, `tun=32`, and `forward_ping_ok=32`, and Gate E-Core 56 UE A/B Launch-to-TUN comparison passes.
- The full 64 UE staged stress runtime validation is still pending as Gate E-Stretch; it does not block SDK v1.
- Exact O-RAN and 3GPP clause mapping remains `[Needs Verification]`.
