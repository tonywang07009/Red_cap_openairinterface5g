# Work Daily Log
## Session Metadata
- Date: 2026-05-07 12:27
- Agent Session ID: N/A
- Task Slug: m1-m2-m3-m4b-unit-regression-pass
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md
- Milestone File: milestones/M1_phy_constraints.md, milestones/M2_rrc_sib1_redcap.md, milestones/M3_bwp_coreset_ra.md, milestones/M4B_drx_edrx_psm.md
- Validation File: validation/test_matrix.md
- Task ID: M1-T3, M2-T1, M3-T2, M4B-T1
- Batch: A / C

## Milestone & Sub-task Reference
- Milestone: M1 PHY Constraints / M2 RRC SIB1 RedCap / M3 BWP CORESET RA / M4-B DRX eDRX PSM
- Sub-task: Re-run and pass unit regression set for M4B, M3, M2, and M1
- Status: [COMPLETED]

## What Was Done
- Built the unit test targets for M1/M2/M3/M4B:
  - test_nr_frame_params
  - test_nr_redcap_coreset0
  - test_nr_redcap_bwp
  - test_nr_ue_redcap_bwp
  - test_nr_rrc_redcap
  - test_nr_ue_drx
  - test_nr_rrc_lowpower
  - test_nr_nas_lowpower
- Fixed stale M1 unit-test expectation in openair1/PHY/INIT/tests/test_nr_frame_params.cpp:
  - gNB RedCap common grid over 20 MHz is now allowed because the RedCap-specific BWP / UE path enforces the 20 MHz limit.
  - Added UE-side over-20-MHz death coverage to keep RedCap PRB cap validation intact.
- Updated validation/test_matrix.md:
  - UT-M3-002 moved to [x].
  - UT-M4B-001, UT-M4B-002, and UT-M4B-003 moved to [x].
- Re-ran the complete M1/M2/M3/M4B CTest set and confirmed 8/8 pass.

## 3GPP Spec Clauses Referenced
- TS 38.101-1 Section 5.3 — FR1 channel bandwidth / PRB limits for RedCap BWP context. [Needs Verification]
- TS 38.306 Section 4 — RedCap UE capability constraints, including reduced bandwidth and antenna assumptions. [Needs Verification]
- TS 38.331 Section 6.3.1 / 6.3.2 — SIB1 structure and RedCap-related fields. [Needs Verification]
- TS 38.213 Section 13 — Type0 CSS / CORESET#0 behavior. [Needs Verification]
- TS 38.321 Section 5.7 — Connected DRX behavior.
- TS 24.501 PSM timer behavior — exact clause pending. [Needs Verification]

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Initial all-target build | FAIL | tests preset support dependency | Failed at check_vcd due known LeakSanitizer under ptrace issue. |
| All-target build retry | PASS | 8 unit targets | Log: test_log/build_logs/build_m1_m2_m3_m4b_unit_targets_2026-05-07_12-25-02_lsanoff.log |
| test_nr_frame_params rebuild | PASS | M1 PHY frame params / RedCap PRB and antenna checks | Log: test_log/build_logs/build_test_nr_frame_params_2026-05-07_12-27-08_m1-unit-align.log |
| First CTest run | FAIL | 7/8 passed | test_nr_frame_params had stale gNB common-grid death expectation. |
| Final CTest run | PASS | 8/8 tests passed | Log: test_log/compiler_logs/ctest_m1_m2_m3_m4b_units_2026-05-07_12-27-17_after-m1-align.log |
| Container image rebuild | N/A | Unit-test-only task | No runtime image rebuild required. |
| RFsim runtime | N/A | Unit-test-only task | M5 runtime remains separate. |

## Known Issues / Blockers
- M4B runtime / flow validation remains open:
  - FV-M4B-DRX is not marked passed.
  - RT-M4B-001 / RT-M4B-002 were not executed in this unit-test task.
- Exact 3GPP clause mappings for several RedCap/eDRX/PSM rows remain [Needs Verification] in the traceability matrix.

## Next Step
- Use the now-passing M1/M2/M3/M4B unit baseline as the stable regression gate before returning to M5 staged runtime scaling.
