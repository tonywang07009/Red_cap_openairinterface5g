# Workflow v3 Follow-up Ledger

## Purpose

- Record dApp/xApp SDK test gaps without reopening completed `redcap_oran_sdk_workflow_v3` tasks.
- Keep runtime blockers separate from static SDK/API validation.

## Open Follow-ups

| ID | Source Gate | Gap | Next Pull Item | Status |
|---|---|---|---|---|
| DXV-FU-003 | Gate E | 56 UE / 5 MHz BWP not validated | run only after Gate D passes | [pending] |
| DXV-FU-004 | Gate D/E | PDCCH command path still needs runtime and clause verification | validate Gate D RFsim log and verify TS 38.212/38.214 mapping | [pending] |
| DXV-FU-005 | Gate C | Official `tl_expected` dependency was not fetched; Gate C used local test shim | replace shim with official cache/network dependency before production dependency claims | [pending] |
| DXV-FU-007 | Gate D/E | dApp policy rewrite of PUCCH/PUSCH allocation not implemented | implement policy apply after Gate D marker runtime passes | [pending] |
| DXV-FU-009 | Gate D | Pre-fix 5 MHz run showed gNB/UE RedCap RA DCI bit-length mismatch; source fix and gNB/UE builds passed, but post-fix RFsim is blocked by workspace credits | rebuild images, recreate gNB + UE2, then rerun `gate_d_rfsim_marker_check.py --gnb-log <gNB-log> --ue-log <UE-log> --require-runtime --require-bwp-mhz 5` | [pending] |

## Closed Follow-ups

| ID | Source Gate | Resolution | Evidence |
|---|---|---|---|
| DXV-FU-001 | Gate C | E3 POSIX loopback and latency benchmark passed with local `tl_expected` test shim | `test_log/compiler_logs/gate_c_libe3_runtime_test_role_pair_posix_2026-07-06_11-58-08.log`; `test_log/compiler_logs/gate_c_libe3_runtime_test_bench_full_loop_latency_2026-07-06_11-58-23.log` |
| DXV-FU-002 | Gate D | dApp/gNB source marker hook implemented in the ULSCH/PUSCH/PDCCH path | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c`; `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_d_rfsim_marker_check.py` |
| DXV-FU-006 | Gate D | PUCCH marker hook mapped and implemented after `nr_configure_pucch()` | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_uci.c`; `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_d_rfsim_marker_check.py` |
| DXV-FU-008 | Gate D/E | 5 MHz BWP RFsim gNB profile added and statically checked | `ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml`; `gate_d_rfsim_marker_check.py --require-bwp-mhz 5` |
