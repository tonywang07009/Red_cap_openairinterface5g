# Workflow v3 Follow-up Ledger

## Purpose

- Record dApp/xApp SDK test gaps without reopening completed `redcap_oran_sdk_workflow_v3` tasks.
- Keep runtime blockers separate from static SDK/API validation.

## Open Follow-ups

| ID | Source Gate | Gap | Next Pull Item | Status |
|---|---|---|---|---|
| DXV-FU-003 | Gate E | full 64 UE staged 5 MHz-to-20 MHz BWP runtime not validated | run a one-UE 51PRB RF/SSB alignment smoke first, then rerun the 64 UE / 20 MHz proxy stage and collect expansion/control evidence | [pending] |
| DXV-FU-004 | Gate D/E | PDCCH command path still needs exact clause verification | verify TS 38.212/38.214 mapping before public spec claims | [pending] |
| DXV-FU-005 | Gate C | Official `tl_expected` dependency was not fetched; Gate C used local test shim | replace shim with official cache/network dependency before production dependency claims | [pending] |
| DXV-FU-007 | Gate D/E | dApp access-pressure policy helper is implemented, but runtime application to connected scheduling is not validated | apply the policy after Gate D marker runtime passes and compare collision proxy before/after | [pending] |
| DXV-FU-010 | Gate D/E | CSI-RS/SRS enabled 5 MHz run asserts in `encode_cellGroupConfig()` on `nzp-CSI-RS-ResourceToAddModList` | decide whether Gate E uses the no-CSI/SRS RFsim workaround or fixes CSI-RS/SRS first | [pending] |
| DXV-FU-014 | Gate E | 51 PRB / 20 MHz proxy full64 run used 106PRB UE RF/SSB defaults and failed before synchronization | rerun one-UE 51PRB smoke after the wrapper RF/SSB default fix, then rerun full64 if sync/attach/PDU/TUN passes | [pending Docker credits] |

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
