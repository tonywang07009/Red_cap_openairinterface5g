# Work Daily Log
## Session Metadata
- Date: 2026-04-30 12:28
- Agent Session ID: N/A
- Task Slug: m3t2-gnb-redcap-msg1-marking
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md
- Task ID: M3-T2
- Batch: B

## Milestone & Sub-task Reference
- Milestone: [M3-T2 CORESET#0 Case A/B host validation]
- Sub-task: [gNB RA context RedCap Msg1 marking]
- Status: [COMPLETED]

## What Was Done
- Used [symdex MCP] to locate [nr_initiate_ra_proc()], [NR_RA_t], [preamble_index], and existing RedCap RACH helper paths.
- Updated `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.h`.
- Added `nr_redcap_is_msg1_preamble()` API for checking whether a received Msg1 preamble belongs to [FeatureCombinationPreambles-r17.redCap-r17].
- Updated `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c`.
- Implemented per-SSB preamble partition detection with [startPreambleForThisPartition-r17] and [numberOfPreamblesPerSSB-ForThisPartition-r17].
- Updated `openair2/LAYER2/NR_MAC_gNB/nr_mac_gNB.h`.
- Added `NR_RA_t.is_redcap_msg1` to persist the Msg1 early indication in the gNB RA context.
- Updated `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c`.
- Set `ra->is_redcap_msg1` inside `nr_initiate_ra_proc()` immediately after loading the serving cell RACH config.
- Added a gNB log marker: `[RedCap RA][gNB Msg1] detected RedCap preamble index ...`.
- Updated `openair2/LAYER2/NR_MAC_gNB/tests/test_nr_redcap_bwp.cpp`.
- Added unit coverage for single-SSB and per-SSB RedCap Msg1 preamble detection.

## 3GPP Spec Clauses Referenced
- TS 38.321 Random Access procedure — RedCap early indication through Msg1/MsgA/Msg3 resources. Exact clause: [Needs Verification].
- TS 38.331 ASN.1 `FeatureCombinationPreambles-r17` — contains [redCap-r17], [startPreambleForThisPartition-r17], and [numberOfPreamblesPerSSB-ForThisPartition-r17]. Exact clause: [Needs Verification].
- TS 38.213 Section 13 — CORESET#0 / Type0-PDCCH CSS context for later Msg2 Case B scheduling. Relevance for next task.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `nr-softmodem` source build | PASS | gNB MAC RA compile/link | Log: `test_log/build_logs/build_nr-softmodem_2026-04-30_12-26-53_m3t2-msg1-redcap-mark-retry.log` |
| `test_nr_redcap_bwp` build | PASS | RedCap BWP/RACH helper unit binary | Log: `test_log/build_logs/build_test_nr_redcap_bwp_2026-04-30_12-27-21_m3t2-msg1-redcap-mark.log` |
| `ctest -R test_nr_redcap_bwp --output-on-failure` | PASS | 1 CTest, includes new Msg1 partition checks | Log: `test_log/compiler_logs/ctest_test_nr_redcap_bwp_2026-04-30_12-27-49_m3t2-msg1-redcap-mark.log` |
| RFsim runtime | NOT RUN | Runtime attach / Msg2 behavior | Deferred until [Msg2 scheduler RedCap gate] is implemented |

## Known Issues / Blockers
- [Msg2 scheduler] still does not gate [coreset_id=1 / BWP51] by `ra->is_redcap_msg1`.
- Exact 3GPP clause number for [featureCombinationPreamblesList-r17] remains [Needs Verification].
- `clang-format` is not installed in this environment, so formatting was manually kept consistent.
- There are unrelated pre-existing worktree changes in `agent_doc/Project_management/Simluation_v2.md`, `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/.env`, and submodule metadata; they were not touched.

## Next Step
- Implement [Msg2 scheduler RedCap gate] so Case B uses RedCap [CORESET/BWP] only when `ra->is_redcap_msg1` is true.
