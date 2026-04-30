# Work Daily Log
## Session Metadata
- Date: 2026-04-30 21:13
- Agent Session ID: N/A
- Task Slug: m3t2-runtime-scc-redcap-bwp-sync
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: [M3-T2 RedCap Msg1/Msg2 Case B runtime validation]
- Sub-task: [Msg2 scheduler RedCap gate] and [RFsim Case B runtime validation]
- Status: [IN-PROGRESS]

## What Was Done
- Updated `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` and `nr_radio_config.h` to add `nr_redcap_configure_runtime_scc()`.
- Updated `openair2/LAYER2/NR_MAC_gNB/config.c` so gNB MAC runtime [ServingCellConfigCommon] receives RedCap initial DL/UL BWP clones before scheduler use.
- Preserved prior Msg1 preamble-domain fix in `nr_mac_redcap_bwp.c`, `gNB_scheduler_RA.c`, and `test_nr_redcap_bwp.cpp`.
- Rebuilt `nr-softmodem` successfully after C changes.
- Re-ran `test_nr_redcap_bwp`: 15/15 assertions passed; clean CTest PASS with `LSAN_OPTIONS=detect_leaks=0`.
- Rebuilt local Docker images with `ci-scripts/redcap_rebuild_local_oai_images.sh`.
- Re-ran RFsim Case B using `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap` and generated config `test_log/runtime_configs/gnb.redcap_case-b_disabled_2026-04-30_21-07-16.yaml`.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.2.2.4.2 — SIB1 and ServingCellConfigCommon delivery path for initial BWP configuration.
- TS 38.331 Section 6.3.2 — RACH-ConfigCommon and feature-associated preamble partition context.
- TS 38.321 Section 5.1.4 — Random Access Response reception behavior.
- TS 38.306 Section 4.2.21.1 — RedCap UE capability context.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| nr-softmodem source build | PASS | gNB C source | Escalated build passed after sandbox ccache failure. |
| test_nr_redcap_bwp | PASS | 15/15 assertions | Plain CTest hit LeakSanitizer ptrace issue; rerun with leak detection off passed. |
| Docker image rebuild | PASS | ran-build/oai-gnb/oai-nr-ue | Local RedCap runtime images rebuilt from workspace. |
| RFsim Case B runtime | FAIL | UE1 attach PASS, UE2 attach FAIL | UE2 did not receive IP; scenario failed at [333332 Attach UE2 RedCap]. |
| gNB Msg1 RedCap marker | PASS | Runtime log | `[RedCap RA][gNB Msg1]` present. |
| gNB Msg2 gate | PASS | Runtime log | `[RedCap RA][gNB Msg2 gate]` present with `coreset_id=1`, `dl_bwp_size=51`, `ul_bwp_size=51`. |
| gNB Msg2 DCI | PASS | Runtime log | `[RedCap RA][gNB Msg2 DCI]` present with `coreset_id=1 / BWP51`. |
| UE2 RA-RNTI monitoring | PASS | Runtime log | UE2 monitors `coreset_id=1 / BWP51`. |
| UE2 RAR decode | FAIL | Runtime log | UE2 reports `Received a RAR-Msg2 but LDPC decode failed` and `RAR reception failed`. |

## Known Issues / Blockers
- RFsim Case B still fails at UE2 attach.
- The previous blocker `[initialDownlinkBWP-RedCap-r17 is not configured]` is fixed.
- Current blocker moved to `[RAR-Msg2 PDSCH/LDPC decode]`: DCI and BWP/CORESET are aligned, but UE2 decodes all-zero RAR PDU and fails LDPC.
- Need inspect Msg2 PDSCH PDU/BWP/RB mapping, TBS/DMRS/TDA, and whether gNB PDSCH PDU parameters match UE RedCap BWP assumptions.

## Next Step
- Continue at [RFsim Case B RAR-Msg2 decode validation]: inspect gNB `prepare_dl_pdus()` / PDSCH PDU fields and UE PDSCH decode path for RedCap Msg2 Case B, focusing on all-zero PDU / LDPC decode failure.
