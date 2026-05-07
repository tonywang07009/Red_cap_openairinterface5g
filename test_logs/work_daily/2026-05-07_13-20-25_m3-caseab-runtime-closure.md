# Work Daily Log
## Session Metadata
- Date: 2026-05-07 13:20
- Agent Session ID: N/A
- Task Slug: m3-caseab-runtime-closure
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md
- Milestone File: milestones/M3_bwp_coreset_ra.md
- Validation File: validation/test_matrix.md
- Task ID: M3-T2
- Batch: B

## Milestone & Sub-task Reference
- Milestone: M3 BWP CORESET RA
- Sub-task: CORESET#0 Case A/B host runtime evidence completion
- Status: [COMPLETED]

## What Was Done
- Re-ran [RT-M3-CASEB] with local images and [REDCAP_E2_AGENT_MODE=disabled].
- Re-ran [RT-M3-CASEA] after stale CN/RAN compose cleanup to preserve fresh artifacts.
- Preserved Case A artifacts under `test_log/runtime_artifacts/m3_casea_2026-05-07_13-15-07/`.
- Preserved Case B artifacts under `test_log/runtime_artifacts/m3_caseb_2026-05-07_13-10-12/`.
- Updated `project_plan.md` to mark [M3] and [M3-T2] complete and move active focus to [M4-B].
- Updated `validation/test_matrix.md` to mark [FV-M3-001] and [RT-M3-CASEA] complete.
- Updated `milestones/M3_bwp_coreset_ra.md` and `checklist/redcap_milestone_validation_checklist.md` with closure evidence.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 6.3.2 — RedCap initial DL/UL BWP fields and SIB1 mapping. Exact subsection: [Needs Verification].
- TS 38.213 Section 13 — Type0 CSS / CORESET#0 monitoring behavior. Exact subsection: [Needs Verification].
- TS 38.321 Section 5.1.4 — Random Access Response reception. Exact subsection: [Needs Verification].
- TS 38.321 Section 5.1.5 — contention resolution / Msg4 flow. Exact subsection: [Needs Verification].

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Unit baseline M1/M2/M3/M4B | PASS | 8/8 CTest targets | `test_log/compiler_logs/ctest_m1_m2_m3_m4b_units_2026-05-07_12-27-17_after-m1-align.log` |
| RT-M3-CASEA | PASS | RFsim Case A attach, RedCap BWP, ping, UL iperf | Summary: `test_log/report/redcap_runtime_host_summary_case-a_disabled_2026-05-07_13-15-07.md` |
| RT-M3-CASEB | PASS | RFsim Case B attach, edge-aligned common CORESET, ping, UL iperf | Summary: `test_log/report/redcap_runtime_host_summary_case-b_disabled_2026-05-07_13-10-12.md` |
| Source build | N/A | No C/C++ changes in this closure step | Used existing local runtime images |
| Container image rebuild | N/A | No C/C++ changes in this closure step | Existing local images were used |

## Known Issues / Blockers
- First Case A attempt on 2026-05-07 13:02 was blocked by stale Docker CN/RAN network state and is not counted as runtime evidence.
- M5 staged scaling remains deferred: previous Case A reached 26/30, Case B reached 27/30, with RA/Msg4 scheduler load and UE PUCCH common fallback still pending.

## Next Step
- Start [M4-B] DRX/eDRX/PSM flow/runtime boundary closure before returning to [M5] staged mMTC scaling.
