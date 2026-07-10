# RedCap dApp/xApp SDK Test Validation v1

## Project Metadata

- [Project Path]: `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/project_plan.md`
- [OpenSpec Change]: `openspec/changes/redcap-dapp-xapp-sdk-test-validation/`
- [Primary References]: `dev_refer/`
- [Related Workflow]: `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/`
- [Objective]: validate the next RedCap dApp/xApp SDK slice through a two-tier Gate E model before making broader 64 UE stress claims.

## Reference Priority

- [MUST] Use `dev_refer/dapp_dev_need/libe3/` for E3 role, transport, encoding, and SWIG binding expectations.
- [MUST] Use `dev_refer/dapp_dev_need/E3Controller/` for I/Q pipeline, per-slot pipeline, `--num-prbs`, and timing-log expectations.
- [MUST] Use `dev_refer/dapp_dev_need/dApp-library/` for I/Q sample, PRB control, and visualization examples.
- [MUST] Use `dev_refer/dapp_dev_need/dApp-openairinterface5g/` only as a targeted implementation reference, not as a source tree to copy.
- [MUST] Use `dev_refer/xapp_dev_need/` and `openair2/E2AP/flexric/` for xApp design comparison.
- [MUST] Mark exact O-RAN and 3GPP clause mappings `[Needs Verification]` until locally extracted.

## Gate Index

| Gate | Purpose | Acceptance Evidence | Status |
|---|---|---|---|
| Gate A | SDK unit and API contract | Python self-test and C syntax checks | [~] static scaffold |
| Gate B | SWIG evidence boundary | SWIG interface files verified; generated module status reported | [~] definition check only |
| Gate C | E3 loopback | RAN-role and DAPP-role E3 agents exchange indication/control | [x] PASS with local expected shim |
| Gate D | small RFsim marker | 1-2 UE dApp/xApp markers plus gNB-side apply marker | [x] PASS with local image and no-CSI/SRS runtime workaround |
| Gate E-Core | 56 UE dApp A/B access-latency gate | baseline-vs-dApp 56 UE health plus Launch-to-TUN latency comparison | [x] PASS |
| Gate E-Stretch | 64 UE strict upper-bound stress | full64 attach/PDU/TUN/ping/control evidence without gNB restart | [~] non-blocking stretch |

## Current Boundary

- Current static work does not claim [64 UE / 5 MHz-to-20 MHz BWP runtime PASS].
- Gate E is now split into [Gate E-Core] and [Gate E-Stretch]. Gate E-Core is the SDK v1 engineering completion gate; Gate E-Stretch remains a non-blocking upper-bound validation.
- Gate E-Core uses a 56 UE baseline-vs-dApp A/B test on the current 51 PRB expanded-bandwidth proxy. The primary metric is [Launch-to-TUN] access latency: per-UE launch timestamp to first observed `oaitun_ue1`.
- Gate E-Core requires both baseline and dApp-enabled runs to reach `sample=56`, `running=56`, `attach=56`, `pdu=56`, `tun=56`, and `gnb_restart=0`. It also requires per-UE latency CSV evidence, median/p95/max comparison in the report, dApp decision/PRB/PUCCH-pressure markers in the dApp run, and no assert/abort/segfault marker.
- Gate E-Core does not require the dApp-enabled run to be faster as a hard PASS condition in v1. A valid A/B comparison is the required engineering deliverable.
- Gate E-Stretch keeps strict 64 UE validation as research-grade stress evidence only. The latest `attach/pdu/tun=62/64` result is a Stretch blocker, not a Core blocker.
- Current work claims [Gate D small RFsim marker PASS] only under the documented no-CSI/SRS runtime workaround.
- Current work does not claim [dApp access-pressure policy effectiveness under collision load].
- Current Gate E runtime evidence proves the first32 5 MHz stage reaches `attach=32`, `pdu=32`, `tun=32`, `forward_ping_ok=32`, and `gnb_restart=0` after the connected DCI BWP fix. It does not prove the 64 UE / 20 MHz proxy expansion or collision-load access-pressure effectiveness.
- Current full64 20 MHz proxy evidence proves the 51 PRB gNB profile was loaded, but the 2026-07-07 23:39:18 run failed before synchronization because UE RF/SSB defaults remained `3630360000/144` while the gNB 51 PRB profile expected `3617640000/238`.
- Current 2026-07-08 one-UE 51PRB smoke evidence proves the RF/SSB wrapper defaults now reach sync, attach, PDU, TUN, and `gnb_restart=0`; the following full64 run reached 51PRB dApp markers but failed with `sample=64 running=15 attach=59 pdu=59 tun=11 gnb_restart=1 failures=55`.
- Current source fix for the 2026-07-08 UE48 full64 abort makes CSI measurement periodicity use the reused PUCCH reservation UID. Docker image rebuild later succeeded, and the next full64 attempt passed the prior UE48 CSI crash zone but failed with `sample=64 running=0 attach=62 pdu=62 tun=0 failures=65`.
- Current runtime guard fixes for E2 `epoll_wait(EINTR)`, UE invalid CCCH MAC length, and missing `masterCellGroup` RRCSetup input build locally and are in rebuilt images; the post-guard one-UE 51PRB smoke passes with `attach=1`, `pdu=1`, `tun=1`, and `gnb_restart=0`.
- Earlier post-guard full64 runtime reached `sample=64`, `running=64`, `attach=64`, `pdu=64`, `tun=64`, and `gnb_restart=0`, but stayed open because `failures=2`, sampled UL iperf timed out for UE1/UE25, and no xApp control/ACK marker was observed in the monitor logs.
- Current RC control attempt exposed a gNB assert on an unknown/stale RNTI in the RedCap RC write path. The RC write path now rejects malformed or unknown-RNTI control requests instead of aborting, the RNTI selector prefers live dApp MAC markers, the full64 wrapper adds iperf retry support, and local images were rebuilt from these fixes.
- Current RC-control-guard image inspection is no longer blocked. `test_log/compiler_logs/gnb_image_inspect_2026-07-09_rc_control_guard.log` confirms the local `oai-gnb:latest` image contains FlexRIC libraries and the PUCCH budget marker.
- Current post-RC-control-guard one-UE 51PRB smoke evidence shows RF/SSB alignment, sync, PDU session accept, `oaitun_ue1`, and `gnb_restart=0` in `test_log/compiler_logs/mmtc_smoke_2026-07-08_23-29-28_*`.
- Current post-RC-control-guard full64 rerun reached `sample=64`, `running=64`, `attach=62`, `pdu=62`, `tun=62`, `forward_ping_ok=54`, `iperf_ul_ok=1`, `iperf_ul_run=3`, `gnb_restart=0`, and `failures=12`. UE62 and UE64 stayed running/healthy but did not create `oaitun_ue1`; UE8/UE23/UE42/UE44/UE54/UE56/UE59/UE60 failed forward ping; UE25 and UE50 failed all UL iperf retries.
- Current live xApp control path is verified for one selected RNTI after the failed full64 run: `redcap_rc_ctrl_xapp_2026-07-09_00-00-46.log` contains `CONTROL ACK rx`, `redcap_rc_ctrl_xapp_2026-07-09_00-00-46_nearRT-RIC_live_postcontrol.log` contains `CONTROL ACKNOWLEDGE rx`, and `redcap_rc_ctrl_xapp_2026-07-09_00-00-46_gnb_live_postcontrol.log` contains `RedCap UL PRB control RNTI fc38 requested 32 effective 32`.
- Current Gate E-Core runtime evidence proves the 56 UE baseline-vs-dApp Launch-to-TUN comparison: both runs reached `sample=56`, `running=56`, `attach=56`, `pdu=56`, `tun=56`, `gnb_restart=0`, and `failures=0`.
- Gate E-Core latency evidence: baseline median/p95/max `436318/703145/722926 ms`; dApp median/p95/max `441487/708146/728189 ms`; dApp-minus-baseline delta `+5169/+5001/+5263 ms`. This is a valid A/B comparison, not a latency-improvement claim.
- Gate E-Core dApp marker evidence: `test_log/compiler_logs/mmtc_smoke_2026-07-09_10-42-43_gnb.log` contains `RedCap dApp PRB decision` markers and no assert/abort/segfault marker was found by the checker.
- Current core36 pressure implementation adds `redcap_dapp_select_ra_pressure_priority`, `select_core36_pressure_priority.py`, `MMTC_STAGE_PROFILE=core36_pressure`, one-call zero-gap batch UE start, wrapper-level `MMTC_DAPP_STOP_NON_PRIORITY`, and `gate_e_64ue_stage_check.py --stage core36-pressure`.
- Current true batch-start core36 runtime evidence creates pressure: baseline and dApp runs both reached `sample=36`, `running=36`, `attach=17`, `pdu=17`, `tun=17`, `gnb_restart=0`, and `failures=19`.
- Core36 batch-start latency evidence over successful TUN rows: baseline median/p95/max `37651/43189/44453 ms`; dApp median/p95/max `37687/43991/44369 ms`. This is valid A/B evidence, not mitigation or latency-improvement evidence.
- Core36 selector evidence selected UE36 from baseline because it had the highest observed `ra_retry_count=452` and no TUN. The selected UE still had no TUN in the dApp run, so the priority decision did not improve access success.
- Core36 STOP boundary: the wrapper emitted `[RedCap dApp wrapper STOP] ACK selected_ues=36 action=pause` in the true batch-start dApp run. Prior STOP+iperf evidence paused 35 non-selected UE containers, but sampled UL iperf timed out; do not report traffic-relief PASS until the iperf path passes.
- Current core36 pressure boundary: dApp does not mitigate the true batch-start access pressure in current evidence.
- Current post-boundary scheduler update: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c` now supports `OAI_REDCAP_DAPP_RA_RETRY_PRIORITY=1`, which schedules `nrRA_Msg3_retransmission` before new `nrRA_Msg2` entries. This is a gNB-visible RA-state priority hook, not a direct UE36-at-Msg1 selector.
- Post-hook readiness evidence: `test_log/build_logs/build_nr-softmodem_2026-07-10_02-14-47_ra-retry-priority.log` and `test_log/build_logs/rebuild_local_oai_images_2026-07-10_02-15-34_ra-retry-priority.log`.
- Post-hook runtime boundary: fresh core36 A/B rerun was not captured because Docker compose escalation for the runtime run was rejected when workspace credits were exhausted.
- Current SDK additions are test-facing helpers for priority hints, PRB allocation decisions, and dApp access-pressure policy decisions.
- The dApp remains the local apply/reject boundary; xApp only emits UE priority hints.

## Validation Commands

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/check_dapp_xapp_sdk_test_validation.py
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/dapp_xapp_sdk_contract_selftest.py
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py --try-configure
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py --try-configure --allow-fetch
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_d_rfsim_marker_check.py
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_e_64ue_stage_check.py
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_e_64ue_stage_check.py --stage core56-ab --baseline-summary-log <baseline-summary> --dapp-summary-log <dapp-summary> --baseline-latency-log <baseline-latency.csv> --dapp-latency-log <dapp-latency.csv> --dapp-gnb-log <dapp-gnb-log>
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_e_64ue_stage_check.py --stage first32 --gnb-log test_log/compiler_logs/mmtc_smoke_<timestamp>_gnb.log --summary-log test_log/compiler_logs/mmtc_stage_scan_<timestamp>_summary.log
openspec validate redcap-dapp-xapp-sdk-test-validation --strict
```

## Next Runtime Pull

- Gate E-Core 56 UE A/B access-latency comparison is complete; return to 64 UE Stretch work only when strict upper-bound evidence is explicitly needed.
- The lighter core36 pressure gate with 56 UE topology, 36 sampled UE, one-call batch start, `MMTC_UE_START_GAP=0`, `MMTC_ADAPTIVE_BURST_ON_ZERO_GAP=0`, and baseline-derived `MMTC_DAPP_PRIORITY_UES` now has A/B evidence checked by `--stage core36-pressure`.
- Next runtime pull should rerun core36 A/B with `OAI_REDCAP_DAPP_RA_RETRY_PRIORITY=1` and diagnose the STOP+sampled-iperf timeout path.
- Baseline profile: `MMTC_TOTAL_UES_TARGET=56`, `MMTC_STAGE_LIST=56`, `MMTC_START_XAPP=0`, `OAI_REDCAP_DAPP_GATE_D_MARKER=0`, `MMTC_N_RB_DL=51`, `MMTC_IPERF_ENABLE=0`, and the no-CSI/SRS RFsim workaround.
- dApp profile: same RF/CN/UE profile, with `MMTC_START_XAPP=1` and `OAI_REDCAP_DAPP_GATE_D_MARKER=1`.
- Gate E-Core evidence: baseline summary `test_log/compiler_logs/mmtc_stage_scan_2026-07-09_10-27-10_summary.log`, dApp summary `test_log/compiler_logs/mmtc_stage_scan_2026-07-09_10-42-43_summary.log`, baseline latency `test_log/compiler_logs/mmtc_smoke_2026-07-09_10-27-10_access_latency.csv`, dApp latency `test_log/compiler_logs/mmtc_smoke_2026-07-09_10-42-43_access_latency.csv`, dApp gNB marker log `test_log/compiler_logs/mmtc_smoke_2026-07-09_10-42-43_gnb.log`, and report `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/report/gate_e_core56_ab_latency_2026-07-09.md`.
- Core36 evidence: baseline summary `test_log/compiler_logs/mmtc_stage_scan_2026-07-10_01-58-27_summary.log`, dApp summary `test_log/compiler_logs/mmtc_stage_scan_2026-07-10_02-00-43_summary.log`, baseline latency `test_log/compiler_logs/mmtc_smoke_2026-07-10_01-58-27_access_latency.csv`, dApp latency `test_log/compiler_logs/mmtc_smoke_2026-07-10_02-00-43_access_latency.csv`, dApp gNB marker log `test_log/compiler_logs/mmtc_smoke_2026-07-10_02-00-43_gnb.log`, latest STOP+iperf blocker log `test_log/compiler_logs/mmtc_stage_scan_2026-07-10_01-51-15_ue36.log`, and report `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/report/gate_e_core36_pressure_2026-07-10.md`.
- Core36 post-hook evidence currently stops at build/image readiness; do not reuse the `2026-07-10_02-00-43` dApp run as retry-priority proof because its summary lacks `dapp_ra_retry_priority=1`.
- Replace the Gate C local `tl_expected` shim with official `tl_expected` cache/network access before treating the libe3 build as production dependency evidence.
- Use `ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml` for the 5 MHz BWP run. It keeps the 106 PRB RF carrier stable and makes BWP1 plus RedCap DL/UL initial BWP 12 PRBs at 30 kHz SCS `[Needs Verification]`.
- Latest Gate D 5 MHz RFsim run evidence:
  - gNB log: `test_log/runtime_logs/gate_d_5mhz_gnb_2026-07-06_17-16-57.log`.
  - UE2 log: `test_log/runtime_logs/gate_d_5mhz_ue2_2026-07-06_17-16-57.log`.
  - gNB observed `[RedCap RA][gNB Msg2 BWP selected]` with `dl_bwp_size 12` and `ul_bwp_size 12`.
  - UE2 observed `SIB1 RedCap initial BWP decision` and applied DL/UL BWP size `12`.
  - Root-cause evidence: old runtime logs show RedCap RA DCI bit-length mismatch, gNB `dci_bits 35` versus UE `dci_bits 39`.
  - Source fix: gNB and UE now align RedCap Case B RA common DCI size to the current 12 PRB DL BWP.
  - Build evidence: `test_log/build_logs/build_nr-softmodem_2026-07-06_17-28-49_gate-d-dci-bits.log` and `test_log/build_logs/build_nr-uesoftmodem_2026-07-06_17-29-03_gate-d-dci-bits.log`.
  - Access-pressure policy evidence: Python SDK self-check, dApp/xApp contract self-test, and C syntax check now cover low/medium/high pressure mapping.
  - Post-rebuild evidence: `test_log/build_logs/rebuild_local_oai_images_2026-07-07_00-35-33_dapp_access_pressure_policy.log`.
  - Gate D PASS evidence: `test_log/runtime_logs/gate_d_access_pressure_gnb_2026-07-07_00-47_local_no_csirs_srs.log` and `test_log/runtime_logs/gate_d_access_pressure_ue2_2026-07-07_00-47_local_no_csirs_srs.log`.
  - Gate D PASS command used local images plus `MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0"`.
  - Gate D checker passed with `--require-runtime --require-bwp-mhz 5`.
  - Baseline blocker remains: with CSI-RS/SRS enabled, gNB asserts in `encode_cellGroupConfig()` on `nzp-CSI-RS-ResourceToAddModList` before stable connected-scheduling evidence.
- Treat the current ULSCH/PUCCH hooks as marker hooks only; runtime application of the dApp access-pressure policy remains pending until a collision-load scenario is connected.
- Gate E preflight evidence:
  - 64 UE RFsim overlay generated by `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh 64`.
  - RFsim test topology is based on `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml` plus `docker-compose.mmtc.yml`.
  - CN/AMF topology is based on `/home/tonywang/OAI/oai-cn5g/docker-compose.yaml`; compose config lists `oai-amf`, `mysql`, `oai-smf`, and `oai-upf`.
  - CN DB overlay generated by `redcap_interface/generate_mmtc_cn_db_overlay.sh 64`.
  - Preflight checker PASS: `gate_e_64ue_stage_check.py`.
  - The checker confirms UE1..UE64 compose services, UE1..UE64 RedCap UICC configs, UE64 IMSI in the generated SQL overlay, 5 MHz/12 PRB first-stage profile, and 51 PRB 20 MHz proxy profile `[Needs Verification]`.
- Gate E first32 runtime attempt:
  - Command used local rebuilt images, 64 UE overlay, 32 sampled UE, 5 MHz / 12 PRB profile, xApp enabled, and the no-CSI/SRS RFsim workaround.
  - Summary log: `test_log/compiler_logs/mmtc_stage_scan_2026-07-07_11-11-52_summary.log`.
  - gNB log: `test_log/compiler_logs/mmtc_smoke_2026-07-07_11-11-52_gnb.log`.
  - Result: `[SUMMARY] sample=32 running=32 attach=0 pdu=0 tun=0 gnb_restart=0 failures=32`.
  - Positive evidence: `260` `[RedCap dApp Gate E][PUCCH pressure]` markers and `0` assert/abort/segfault markers.
  - xApp/RIC evidence: E42 setup, two RC subscriptions, and four RC Indications appeared in the saved Docker logs; no RIC Control request/ACK was observed.
  - Current blocker: repeated Msg4/RRC Setup failures on the 12 PRB BWP, with `693` `RA Procedure failed at Msg4` / `Msg4 vrb_map fail` markers.
- Gate E first32 DL TDA fix attempt:
  - Source fix: `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` rebuilds the RedCap initial DL BWP PDSCH TDA list for the 12 PRB BWP instead of cloning the 106 PRB initial BWP TDA list.
  - Build evidence: `test_log/build_logs/build_nr-softmodem_2026-07-07_11-38-37_gate-e-redcap-tda.log`.
  - Local image rebuild evidence: `test_log/build_logs/rebuild_local_oai_images_2026-07-07_11-39-43_gate-e-redcap-tda.log`.
  - Summary log: `test_log/compiler_logs/mmtc_stage_scan_2026-07-07_12-14-11_summary.log`.
  - gNB log: `test_log/compiler_logs/mmtc_smoke_2026-07-07_12-14-11_gnb.log`.
  - Result: `[SUMMARY] sample=32 running=32 attach=0 pdu=0 tun=0 gnb_restart=0 failures=32`.
  - Positive evidence: `2` `[RedCap RA][gNB DL TDA]` markers with `first_start_symbol 2`, `0` `Msg4 vrb_map fail` markers, `32` Msg4 ACK markers, and `32` `Send RRC Setup` markers.
  - UE-side evidence: UE1..UE32 each generated `RRCSetupComplete` once.
  - xApp/RIC live Docker log evidence: E42 setup, two RC subscriptions, and RC Indications were observed; no RIC Control request/ACK marker was observed.
  - Current blocker: no UE registration/PDU/TUN evidence; next pull must inspect SRB1/UL-DCCH or post-RRCSetupComplete handling on the 12 PRB BWP.
- Gate E connected DCI BWP runtime rerun:
  - Root cause: after Msg4 ACK, connected common-search-space UL DCI used the regular 51 PRB initial UL BWP RIV width while the UE had applied the 12 PRB RedCap SIB1 initial UL BWP.
  - Source fix: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c` now preserves RedCap initial DL/UL BWP start/size for connected DCI through `apply_redcap_initial_bwp_if_needed()`.
  - Source build evidence: `test_log/build_logs/build_nr-softmodem_2026-07-07_12-42-09_gate-e-redcap-dci-bwp_retry.log`.
  - Docker image rebuild evidence: `test_log/build_logs/rebuild_local_oai_images_2026-07-07_23-05-19_gate-e-redcap-dci-bwp_retry2_escalated.log`.
  - Report: `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/report/gate_e_first32_2026-07-07.md`.
  - Summary log: `test_log/compiler_logs/mmtc_stage_scan_2026-07-07_23-18-49_summary.log`.
  - gNB log: `test_log/compiler_logs/mmtc_smoke_2026-07-07_23-18-49_gnb.log`.
  - Result: `sample=32 running=32 attach=32 pdu=32 tun=32 forward_ping_ok=32 gnb_restart=0 failures=0`.
  - gNB evidence: `128` `[RedCap RA][gNB DCI BWP]` markers, `32` `Received RRCSetupComplete`, `32` `Received RRCReconfigurationComplete`, and `32` `PDU Session Setup: ID=10`.
  - UE evidence: UE1..UE32 each generated `RRCSetupComplete`, and no UE Docker log contains `TDA index from DCI 12`.
  - xApp/RIC evidence: `test_log/compiler_logs/mmtc_smoke_2026-07-07_23-18-49_xapp-rc-moni.log` contains E42 setup, two RC subscriptions, `5` RC Indications, and `Test xApp run SUCCESSFULLY`; `..._nearRT-RIC.log` contains E2 setup and `ORAN-E2SM-RC`.
  - Control boundary: no RIC Control request/ACK marker was observed.
- Gate E full64 20 MHz proxy runtime attempt:
  - Report: `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/report/gate_e_full64_20mhz_proxy_2026-07-07.md`.
  - Summary log: `test_log/compiler_logs/mmtc_stage_scan_2026-07-07_23-39-18_summary.log`.
  - gNB log: `test_log/compiler_logs/mmtc_smoke_2026-07-07_23-39-18_gnb.log`.
  - UE evidence: UE1 runtime config used `N_RB_DL: 51`, but the UE command used `-C 3630360000 --ssb 144`; all 64 UE Docker logs contain `synch Failed`.
  - gNB evidence: the 51 PRB profile loaded and gNB reported the matching UE hint `-C 3617640000 -r 51 --numerology 1 --ssb 238 -E`.
  - Result: `sample=64 running=64 attach=0 pdu=0 tun=0 forward_ping_ok=0 gnb_restart=0 failures=64`.
  - Root cause: the 51 PRB gNB profile and UE RF/SSB defaults were mismatched before synchronization, so this run does not test RA collision mitigation, dApp policy effectiveness, CN attach, PDU, or TUN behavior.
  - Source fix: `redcap_interface/bash_library/fc_mmtc_smoke_validation.sh` now auto-applies 51PRB RF defaults when `MMTC_N_RB_DL=51` or `GNB_REDCAP_CONFIG` contains `51PRB`.
  - Prepare-only evidence: `test_log/compiler_logs/mmtc_smoke_prepare_only_2026-07-07_51prb_rf_defaults.log` confirms `MMTC_RF_FREQ=3617640000`, `MMTC_SSB_START=238`, and the 64 UE overlay without starting Docker.
  - Runtime boundary at that time: post-fix Docker rerun was rejected because workspace credits were exhausted. This is superseded by the later one-UE and full64 runtime attempts below.
- Gate E one-UE 51PRB RF/SSB alignment smoke after wrapper/default and image rebuild:
  - gNB log: `test_log/compiler_logs/mmtc_smoke_2026-07-08_12-05-16_gnb.log`.
  - UE log: `test_log/compiler_logs/mmtc_smoke_2026-07-08_12-05-16_ue1_docker.log`.
  - gNB state log: `test_log/compiler_logs/mmtc_smoke_2026-07-08_12-05-16_gnb_state.log`.
  - Result: `sample=1 running=1 attach=1 pdu=1 tun=1 forward_ping_ok=1 reverse_ping_ok=1 gnb_restart=0 failures=0`.
  - Evidence: UE reached `Initial sync successful`, registration attach, PDU session accept, and `oaitun_ue1`; gNB loaded `DLBW 51`; no repeated `synch Failed`, RF/SSB mismatch, or assert/abort marker was observed.
  - dApp evidence: 51PRB PUCCH and UL apply markers appeared without `unsupported_bwp_profile` reject markers.
- Gate E full64 20 MHz proxy runtime attempt after one-UE PASS:
  - Summary log: `test_log/compiler_logs/mmtc_stage_scan_2026-07-08_12-07-24_summary.log`.
  - Stage log: `test_log/compiler_logs/mmtc_stage_scan_2026-07-08_12-07-24_ue64.log`.
  - gNB log: `test_log/compiler_logs/mmtc_smoke_2026-07-08_12-07-24_gnb.log`.
  - Result: `sample=64 running=15 attach=59 pdu=59 tun=11 forward_ping_ok=11 reverse_ping_ok=0 iperf_ul_ok=0 iperf_ul_run=0 gnb_restart=1 failures=55 mode=parallel`.
  - Root cause evidence: gNB aborted around UE48 in `set_csi_meas_periodicity()` with `Assertion (offset < 320) failed!` and `event_asio_agent: Assertion '0' failed`; Docker then restarted the gNB container.
  - Source fix: `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` now calculates CSI report offset from `get_pucch_reservation_uid(scc, curr_bwp, uid, "CSI reporting")`, matching the existing PUCCH reservation reuse used by `verify_radio_configuration()`.
  - Local validation: `gate_e_64ue_stage_check.py` static preflight PASS, `check_dapp_xapp_sdk_test_validation.py` PASS, `git diff --check -- openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` PASS, and `cmake --build --preset default --target nr-softmodem` PASS.
  - CSI/Pucch UID image rebuild evidence: `test_log/build_logs/rebuild_local_oai_images_2026-07-08_17-11-54_gate-e-csi-pucch-uid_retry.log`.
  - Post-CSI-fix one-UE smoke evidence: `test_log/compiler_logs/mmtc_smoke_2026-07-08_17-21-13_gnb.log`, `test_log/compiler_logs/mmtc_smoke_2026-07-08_17-21-13_ue1_docker.log`, and `test_log/compiler_logs/mmtc_smoke_2026-07-08_17-21-13_gnb_state.log`.
  - Post-CSI-fix full64 evidence: `test_log/compiler_logs/mmtc_stage_scan_2026-07-08_17-24-06_summary.log` reports `sample=64 running=0 attach=62 pdu=62 tun=0 forward_ping_ok=0 reverse_ping_ok=0 iperf_ul_ok=0 iperf_ul_run=0 gnb_restart=0 failures=65 mode=parallel`.
  - Post-CSI-fix diagnosis: the prior UE48 CSI offset crash no longer appears, but all UE containers exit, UE24/UE45/UE60 abort on invalid CCCH MAC SDU length, the gNB log shows heavy SR/CSI PUCCH pressure, and direct post-run inspection showed a gNB restart after the script's early state sample.
  - Runtime guard source fixes: `openair2/E2AP/flexric/src/agent/asio_agent.c`, `openair2/LAYER2/NR_MAC_UE/nr_ue_procedures.c`, `openair2/RRC/NR/MESSAGES/asn1_msg.c`, and `openair2/RRC/NR/rrc_gNB.c`.
  - Runtime guard build evidence: `test_log/build_logs/build_gate_e_runtime_guards_2026-07-08_17-46-58.log`.
  - Runtime guard image rebuild evidence: `test_log/build_logs/rebuild_local_oai_images_2026-07-08_17-47-31_gate-e-runtime-guards.log`.
  - Runtime guard one-UE 51PRB smoke evidence: `test_log/compiler_logs/mmtc_smoke_2026-07-08_18-00-40_gnb.log`, `test_log/compiler_logs/mmtc_smoke_2026-07-08_18-00-40_ue1_docker.log`, and `test_log/compiler_logs/mmtc_smoke_2026-07-08_18-00-40_gnb_state.log` report `sample=1 running=1 attach=1 pdu=1 tun=1 forward_ping_ok=1 reverse_ping_ok=1 gnb_restart=0 failures=0`.
  - Post-runtime-guard full64 evidence: `test_log/compiler_logs/mmtc_stage_scan_2026-07-08_22-24-50_summary.log` reports `sample=64 running=64 attach=64 pdu=64 tun=64 forward_ping_ok=64 reverse_ping_ok=0 iperf_ul_ok=1 iperf_ul_run=3 gnb_restart=0 failures=2 mode=parallel`.
  - Post-runtime-guard full64 limitation: UE1 and UE25 sampled UL iperf clients timed out, UE50 sampled UL iperf passed, the xApp monitor completed E42/RC subscription setup without a control/ACK marker, and Gate E still lacks before/after collision-load evidence.
  - RC control failure evidence: `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-08_22-52-46.log` timed out after sending a live control request, and the corresponding gNB live log showed `apply_redcap_ul_prb_control` aborting on `RedCap UL PRB control targeted unknown RNTI`.
  - RC control guard source fixes: `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c` now rejects malformed, no-MAC-instance, and unknown-RNTI RedCap UL PRB control requests without aborting; `redcap_interface/bash_library/fc_send_ul_prb_control.sh` now prefers live dApp MAC marker RNTIs; `redcap_interface/bash_library/fc_mmtc_smoke_validation.sh` and `fc_mmtc_stage_scan.sh` now include sampled iperf retries and server-settle delay.
  - RC control guard local validation: `rtk bash -n` PASS for the touched wrappers, `rtk python3 -m py_compile gate_e_64ue_stage_check.py` PASS, `gate_e_64ue_stage_check.py` static preflight PASS, `git diff --check` PASS for the touched files, and local CMake builds PASS.
  - Runtime checker boundary: the 2026-07-08 22:24:50 full64 logs intentionally remain FAIL in `gate_e_64ue_stage_check.py --stage full64` because `failures=2` and no xApp control/ACK marker exist.
  - RC control guard image rebuild evidence: `test_log/build_logs/rebuild_local_oai_images_2026-07-08_22-58-43_gate-e-rc-control-guard.log` rebuilt local runtime images from the guarded source tree.
  - RC-control-guard image inspection evidence: `test_log/compiler_logs/gnb_image_inspect_2026-07-09_rc_control_guard.log` confirms `oai-gnb:latest` includes FlexRIC libraries and the PUCCH budget marker.
  - Post-RC-control-guard one-UE evidence: `test_log/compiler_logs/mmtc_smoke_2026-07-08_23-29-28_ue1_docker.log` shows 51PRB RF/SSB alignment and initial sync; `..._ue1_tun.log` shows `oaitun_ue1`; `..._smf.log` shows PDU Session ID 10 active; `..._gnb_state.log` shows restart count 0.
  - Post-RC-control-guard full64 evidence: `test_log/compiler_logs/mmtc_stage_scan_2026-07-08_23-31-13_summary.log` reports `sample=64 running=64 attach=62 pdu=62 tun=62 forward_ping_ok=54 reverse_ping_ok=0 iperf_ul_ok=1 iperf_ul_run=3 gnb_restart=0 failures=12 mode=parallel`.
  - Post-RC-control-guard full64 blockers: UE62 and UE64 did not create `oaitun_ue1`; UE8/UE23/UE42/UE44/UE54/UE56/UE59/UE60 failed forward ping; UE25 and UE50 UL iperf clients timed out after retries even though the containers stayed running/healthy.
  - xApp control evidence: `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-09_00-00-46.log` has `CONTROL ACK rx`, `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-09_00-00-46_nearRT-RIC_live_postcontrol.log` has `CONTROL ACKNOWLEDGE rx`, and `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-09_00-00-46_gnb_live_postcontrol.log` has the gNB apply marker.
  - Runtime checker boundary: the post-control full64 evidence still fails `gate_e_64ue_stage_check.py --stage full64` only on summary metrics (`attach=62`, `pdu=62`, `tun=62`, `failures=12`), so it remains Gate E-Stretch context.
- Gate E-Core is closed by the 2026-07-09 56 UE baseline-vs-dApp Launch-to-TUN comparison. The full64 UE62/UE64 PDU/TUN, ping loss, and sampled UL iperf timeout issues remain non-blocking Gate E-Stretch work.
- Keep the no-CSI/SRS RFsim workaround explicit until the CSI-RS/SRS enabled blocker is fixed or accepted as out-of-scope for Gate E.
