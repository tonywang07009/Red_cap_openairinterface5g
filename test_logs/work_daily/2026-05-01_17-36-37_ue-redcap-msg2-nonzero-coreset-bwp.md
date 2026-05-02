# Work Daily Log
## Session Metadata
- Date: 2026-05-01 17:36
- Agent Session ID: N/A
- Task Slug: ue-redcap-msg2-nonzero-coreset-bwp
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: M3-T2 RedCap RA / Msg2 runtime validation
- Sub-task: UE RedCap RA-RNTI DCI 1_0 common SS nonzero CORESET BWP alignment
- Status: [COMPLETED]

## What Was Done
- Modified `openair2/LAYER2/NR_MAC_UE/nr_ue_procedures.c`.
- Added `use_current_bwp_for_ra_common_coreset()` to detect `[RA-RNTI + common SS + nonzero CORESET]`.
- Passed `dci->coreset_type` into DCI extraction so RA-RNTI DCI 1_0 can use the active RedCap DL BWP size for RIV extraction.
- Updated `nr_ue_process_dci_dl_10()` so RedCap Msg2 PDSCH uses `current_DL_BWP->BWPStart/BWPSize` instead of `type0_PDCCH_CSS_config.num_rbs` when decoded from nonzero common CORESET.
- Added an INFO runtime marker: `[RedCap RA][UE Msg2 PDSCH]`.

## 3GPP Spec Clauses Referenced
- TS 38.214 Section 5.1.2.2.2 — downlink resource allocation type 1 / RIV domain for DCI 1_0 common search space behavior.
- TS 38.321 Section 5.1.4 — Random Access Response reception path relevance.
- TS 38.306 RedCap bandwidth capability context — RedCap UE should remain within reduced initial BWP constraints. Needs Verification for exact clause citation in local notes.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `cmake --build --preset default --target nr-uesoftmodem` | PASS | UE source build | Escalated rerun passed after sandbox ccache issue. |
| `ctest -R test_nr_redcap_bwp` | PASS | Existing RedCap BWP helper regression | 1/1 passed; no dedicated UE DCI extraction test exists. |
| Docker image rebuild | PENDING | Runtime packaging | Required before RFsim runtime validation. |
| RFsim Case B runtime | PENDING | End-to-end UE2 RedCap RAR | Next step after Docker image rebuild. |

## Known Issues / Blockers
- No existing unit test directly covers UE RA-RNTI DCI 1_0 RIV extraction for nonzero common CORESET.
- Runtime validation still required to confirm UE2 no longer sees all-zero RAR PDSCH.

## Next Step
- Rebuild local OAI Docker images, rerun RFsim Case B from `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`, and check `[RedCap RA][UE Msg2 PDSCH]`, `Received RAR`, and absence of LDPC decode failure.
