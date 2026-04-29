# Work Daily Log

## Session Metadata
- Date: 2026-04-29 11:57
- Agent Session ID: N/A
- Task Slug: m3t2-coreset0-case-matrix
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: [M3-T2 CORESET#0 Case A/B host runtime evidence]
- Sub-task: [Case A/B RFsim host runtime evidence and RA failure isolation]
- Status: [BLOCKED]

## What Was Done
- Used [symdex] repo index [red_cap_openairinterface5g] for code and text queries.
- Confirmed [Case A] 2-UE RFsim host validation fully passed with UE attach, PDU session, ping, and UL iperf.
- Confirmed [Case B] gNB built [SIB1 RedCap initial DL/UL BWP] and logged [RedCap CORESET#0 Case B edge-aligned PRB allocation].
- Confirmed [Case B] UE2 decoded SIB1 enough to apply [RedCap initial DL BWP] and [RedCap initial UL BWP].
- Isolated [Case B] runtime failure to [TS 38.321 Section 5.1 Random Access]: UE2 repeatedly logs [RAR reception failed], while gNB generates [RA-Msg2 DCI] and then fails in [WAIT_Msg3].
- Ran closest unit-test target [test_nr_redcap_coreset0].
- Wrote report: `test_log/report/m3t2_coreset0_case_matrix_report_2026-04-29_11-57-58.md`.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — RedCap bandwidth/capability limits relevant to the [51 PRB] initial BWP.
- TS 38.331 Section 5.2.2.4.2 — SIB1 acquisition and common configuration delivery.
- TS 38.331 Section 5.6.1.3 — BWP configuration behavior.
- TS 38.321 Section 5.1 — Random Access; current Case B failure occurs before [RRCSetupComplete].

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Case A RFsim host runtime | Pass | UE1/UE2 attach, PDU, ping, iperf | `redcap_runtime_host_summary_case-a_disabled_2026-04-29_11-42-14.md` |
| Case B CORESET/SIB1 evidence | Pass | gNB + UE2 log markers | Case B marker and UE2 RedCap BWP apply found |
| Case B UE2 attach/PDU/ping | Fail | Runtime RA path | UE2 [RAR reception failed]; gNB [WAIT_Msg3] failures |
| Build test_nr_redcap_coreset0 | Pass | Unit-test target build | `build_test_nr_redcap_coreset0_2026-04-29_11-57-43_m3t2.log` |
| CTest test_nr_redcap_coreset0 | Pass | 13 GoogleTest cases | Passed with `LSAN_OPTIONS=detect_leaks=0`; default run failed due [LeakSanitizer under ptrace] |

## Known Issues / Blockers
- [Case B] is not yet full PASS because UE2 cannot complete RA attach.
- Current evidence points to [RA-Msg2 PDCCH/RAR monitoring] under [edge-aligned commonControlResourceSet], not NAS or PDU Session.
- Need a small debug/fix patch around [nr_generate_Msg2] / [prepare_dl_pdus] / UE RA monitoring path.

## Next Step
- Continue mainline with [M3-T2 Case B RA/RAR PDCCH root-cause fix], then rebuild affected OAI targets and rerun [test_nr_redcap_coreset0] plus Case B RFsim host validation.
