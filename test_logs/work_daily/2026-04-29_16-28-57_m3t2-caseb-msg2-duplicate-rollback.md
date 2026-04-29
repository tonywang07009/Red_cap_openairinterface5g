# Work Daily Log
## Session Metadata
- Date: 2026-04-29 16:28
- Agent Session ID: N/A
- Task Slug: m3t2-caseb-msg2-duplicate-rollback
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: [M3-T2 CORESET#0 Case B RA/RAR bottleneck]
- Sub-task: [Rollback unsafe Msg2 duplicate DCI and validate mixed UE runtime]
- Status: [COMPLETED]

## What Was Done
- Removed gNB-side unconditional [Msg2 DCI duplicate] behavior from `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c`.
- Kept diagnostic logging for [gNB Msg2 DCI] and [UE RA DCI cfg].
- Rebuilt `nr-softmodem` after C code modification.
- Rebuilt local OAI runtime images after C code modification.
- Re-ran [Case B / E2 disabled / local images] RFsim validation.

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1 — 4-step Random Access procedure.
- TS 38.331 Section 5.2.2.4.2 — SIB1 acquisition and common configuration.
- TS 38.331 Section 5.3.5 — RRCSetup / UE capability path after successful RA.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| nr-softmodem build | PASS | gNB C patch | `build_nr-softmodem_*_m3t2-remove-msg2-dup.log` |
| test_nr_redcap_bwp | PASS | BWP/CORESET helper | `LSAN_OPTIONS=detect_leaks=0 ctest -R '^test_nr_redcap_bwp$'` |
| local OAI image rebuild | PASS | Runtime images | `oai-gnb:latest`, `oai-nr-ue:latest` rebuilt |
| RFsim Case B UE1 | PASS | Baseline UE attach | UE1 got `10.0.0.2`; non-RedCap check PASS |
| RFsim Case B UE2 | FAIL | RedCap attach | UE2 applies BWP51 but RA/RAR still fails |

## Known Issues / Blockers
- UE2 RedCap Case B attach remains blocked by [RA Msg2 DCI] mismatch:
  - UE2 monitors `coreset_id=1`, `BWPSize=51`.
  - gNB sends Msg2 DCI on `coreset_id=0`, `BWPSize=48`.
- Unconditional duplicate DCI is rejected because it breaks normal UE baseline.

## Next Step
- Design a safe [Case B RedCap RA Msg2] path that preserves normal UE RA and targets RedCap UE2 without global RA-RNTI duplication.
