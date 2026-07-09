# Workflow v3 Follow-up Ledger

## Purpose

- Record dApp/xApp SDK test gaps without reopening completed `redcap_oran_sdk_workflow_v3` tasks.
- Keep runtime blockers separate from static SDK/API validation.

## Open Follow-ups

| ID | Source Gate | Gap | Next Pull Item | Status |
|---|---|---|---|---|
| DXV-FU-003 | Gate E-Stretch | full 64 UE staged 5 MHz-to-20 MHz BWP runtime is now non-blocking upper-bound evidence | rerun full64 only when strict upper-bound runtime evidence or host/runtime telemetry is explicitly requested | [pending] |
| DXV-FU-004 | Gate D/E | PDCCH command path still needs exact clause verification | verify TS 38.212/38.214 mapping before public spec claims | [pending] |
| DXV-FU-005 | Gate C | Official `tl_expected` dependency was not fetched; Gate C used local test shim | replace shim with official cache/network dependency before production dependency claims | [pending] |
| DXV-FU-010 | Gate D/E | CSI-RS/SRS enabled 5 MHz run asserts in `encode_cellGroupConfig()` on `nzp-CSI-RS-ResourceToAddModList` | decide whether Gate E uses the no-CSI/SRS RFsim workaround or fixes CSI-RS/SRS first | [pending] |
| DXV-FU-018 | Gate E-Stretch | post-RC-control-guard xApp/RIC/gNB control path is verified for one selected RNTI, but full64 regressed to `attach/pdu/tun=62/64`, `forward_ping_ok=54`, and `failures=12` | keep this as strict 64 UE Stretch work; do not block SDK v1 Gate E-Core on it | [pending] |

## Closed Follow-ups

| ID | Source Gate | Resolution | Evidence |
|---|---|---|---|
| DXV-FU-001 | Gate C | E3 POSIX loopback and latency benchmark passed with local `tl_expected` test shim | `test_log/compiler_logs/gate_c_libe3_runtime_test_role_pair_posix_2026-07-06_11-58-08.log`; `test_log/compiler_logs/gate_c_libe3_runtime_test_bench_full_loop_latency_2026-07-06_11-58-23.log` |
| DXV-FU-002 | Gate D | dApp/gNB source marker hook implemented in the ULSCH/PUSCH/PDCCH path | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c`; `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_d_rfsim_marker_check.py` |
| DXV-FU-006 | Gate D | PUCCH marker hook mapped and implemented after `nr_configure_pucch()` | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_uci.c`; `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_d_rfsim_marker_check.py` |
| DXV-FU-008 | Gate D/E | 5 MHz BWP RFsim gNB profile added and statically checked | `ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml`; `gate_d_rfsim_marker_check.py --require-bwp-mhz 5` |
| DXV-FU-009 | Gate D | Post-fix RFsim marker validation passed with local rebuilt images and no-CSI/SRS runtime workaround | `test_log/runtime_logs/gate_d_access_pressure_gnb_2026-07-07_00-47_local_no_csirs_srs.log`; `test_log/runtime_logs/gate_d_access_pressure_ue2_2026-07-07_00-47_local_no_csirs_srs.log` |
| DXV-FU-011 | Gate E | RedCap DL TDA rebuild removed the previous Msg4 VRB overlap marker in first32 | `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c`; `test_log/compiler_logs/mmtc_smoke_2026-07-07_12-14-11_gnb.log` |
| DXV-FU-012 | Gate E | Connected DCI BWP source fix received runtime proof: first32 reached attach/PDU/TUN and removed UE-side `TDA index from DCI 12` | `test_log/compiler_logs/mmtc_stage_scan_2026-07-07_23-18-49_summary.log`; `test_log/compiler_logs/mmtc_smoke_2026-07-07_23-18-49_gnb.log` |
| DXV-FU-013 | Gate E | Docker image rebuild for the connected DCI BWP fix completed after escalation was available | `test_log/build_logs/rebuild_local_oai_images_2026-07-07_23-05-19_gate-e-redcap-dci-bwp_retry2_escalated.log` |
| DXV-FU-014 | Gate E | 51PRB RF/SSB wrapper default mismatch resolved; one-UE 51PRB smoke passed sync, attach, PDU, TUN, and no gNB restart after local image rebuild | `test_log/compiler_logs/mmtc_smoke_2026-07-08_12-05-16_gnb.log`; `test_log/compiler_logs/mmtc_smoke_2026-07-08_12-05-16_ue1_docker.log`; `test_log/compiler_logs/mmtc_smoke_2026-07-08_12-05-16_gnb_state.log` |
| DXV-FU-015 | Gate E | CSI report periodicity now uses the reused PUCCH reservation UID; local images were rebuilt and the next full64 run passed the prior UE48 CSI offset crash point before exposing later runtime-pressure blockers | `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c`; `test_log/build_logs/rebuild_local_oai_images_2026-07-08_17-11-54_gate-e-csi-pucch-uid_retry.log`; `test_log/compiler_logs/mmtc_stage_scan_2026-07-08_17-24-06_summary.log` |
| DXV-FU-016 | Gate E | E2 EINTR, RRCSetup missing masterCellGroup, and UE invalid CCCH MAC length guards were rebuilt and full64-tested; the next full64 attempt reached 64 attach/PDU/TUN with no gNB restart before exposing sampled iperf and RC-control evidence gaps | `test_log/build_logs/rebuild_local_oai_images_2026-07-08_17-47-31_gate-e-runtime-guards.log`; `test_log/compiler_logs/mmtc_stage_scan_2026-07-08_22-24-50_summary.log`; `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-08_22-52-46.log` |
| DXV-FU-017 | Gate E | RC-control guard images were inspected and rerun; the guarded xApp/RIC/gNB control path now receives ACK and gNB apply marker instead of aborting on unknown/stale RNTI | `test_log/compiler_logs/gnb_image_inspect_2026-07-09_rc_control_guard.log`; `test_log/compiler_logs/mmtc_smoke_2026-07-08_23-29-28_ue1_docker.log`; `test_log/compiler_logs/mmtc_stage_scan_2026-07-08_23-31-13_summary.log`; `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-09_00-00-46.log`; `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-09_00-00-46_gnb_live_postcontrol.log` |
| DXV-FU-019 | Gate E-Core | 56 UE baseline-vs-dApp Launch-to-TUN comparison passed with valid latency evidence | `test_log/compiler_logs/mmtc_stage_scan_2026-07-09_10-27-10_summary.log`; `test_log/compiler_logs/mmtc_stage_scan_2026-07-09_10-42-43_summary.log`; `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/report/gate_e_core56_ab_latency_2026-07-09.md` |
| DXV-FU-007 | Gate D/E-Core | dApp access-pressure policy helper impact is now measured by 56 UE A/B Launch-to-TUN comparison; the result is valid comparison evidence, not improvement evidence | `test_log/compiler_logs/mmtc_smoke_2026-07-09_10-27-10_access_latency.csv`; `test_log/compiler_logs/mmtc_smoke_2026-07-09_10-42-43_access_latency.csv`; `test_log/compiler_logs/mmtc_smoke_2026-07-09_10-42-43_gnb.log` |
