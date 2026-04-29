# Work Daily Log
## Session Metadata
- Date: 2026-04-29 12:36
- Agent Session ID: N/A
- Task Slug: m3t2-caseb-ra-dci-mismatch
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: [M3-T2 CORESET#0 Case A/B host runtime evidence]
- Sub-task: [Case B RA/RAR DCI mismatch diagnosis]
- Status: [COMPLETED]

## What Was Done
- Added [UE RA-RNTI DCI config] diagnostics in `openair2/LAYER2/NR_MAC_UE/nr_ue_dci_configuration.c`.
- Added [gNB Msg2 DCI] diagnostics in `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c`.
- Removed the previous diagnostic [UE fallback CORESET#0 monitoring] behavior because runtime showed it did not resolve attach.
- Kept the valid unit-test link fix in `openair2/LAYER2/NR_MAC_UE/tests/CMakeLists.txt`.
- Rebuilt [nr-uesoftmodem] and [nr-softmodem].
- Ran [test_nr_ue_ra_procedures].
- Rebuilt local runtime images [ran-build], [oai-gnb], and [oai-nr-ue].
- Re-ran [Case B RFsim host validation].
- Confirmed mismatch:
  - [gNB Msg2 DCI] uses [coreset_id=0, BWPSize=48].
  - [UE RedCap RA DCI config] uses [coreset_id=1, BWPSize=51].

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.2.2.4.2 — RedCap initial BWP is signaled through SIB1 extension fields.
- TS 38.321 Section 5.1.4 — UE processes [RAR] after RA-RNTI monitoring during response window.
- TS 38.213 Section 13 — Type0 CSS / CORESET#0 monitoring resource selection.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| nr-uesoftmodem build | PASS | UE MAC DCI diagnostics | Escalated build due sandbox ccache path |
| nr-softmodem build | PASS | gNB RA Msg2 diagnostics | Escalated build due sandbox ccache path |
| test_nr_ue_ra_procedures | PASS | UE RA unit test | `LSAN_OPTIONS=detect_leaks=0` |
| local OAI images rebuild | PASS | Runtime container binaries | ran-build / oai-gnb / oai-nr-ue |
| Case B RFsim host validation | FAIL | UE/gNB/CN runtime | UE1 attach OK; UE2 RedCap attach FAIL |

## Known Issues / Blockers
- [Case B RA/RAR blocker]：gNB sends Msg2 DCI on [legacy CORESET#0/BWP48] while RedCap UE monitors [Case B commonControlResourceSet id=1/BWP51].
- [Normal UE compatibility risk]：A simple global switch to RedCap BWP for all RA may break UE1 legacy attach.

## Next Step
- Implement a gNB-side [Case B Msg2 scheduling fix] that covers RedCap [commonControlResourceSet id=1 / BWP51] while preserving normal UE legacy [CORESET#0 / BWP48] RA.
