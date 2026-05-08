# M6 Evidence Package Summary

## 1. Technical Background
- [M6] packages the RedCap/mMTC evidence produced by M1 through M5 into a traceable documentation set.
- The accepted mMTC runtime target is now [56 RedCap UE] under Case B static CN discovery, with `56/56` attach / PDU / tunnel / forward ping.
- [64 UE] was evaluated as an upper-bound experiment and classified as [gNB runtime restart / SIGKILL threshold], not as CN auth / SMF discovery failure.
- This report does not introduce new protocol behavior. It links preserved evidence, reports test status, and keeps uncertain 3GPP clause mappings marked as [Needs Verification].

## 2. Key Documents / Components
- [Project plan]: `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md`.
- [Validation matrix]: `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/validation/test_matrix.md`.
- [Runtime checklist]: `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/validation/runtime_checklist.md`.
- [Spec traceability]: `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/validation/spec_traceability_matrix.md`.
- [Milestone checklist]: `checklist/redcap_milestone_validation_checklist.md`.

## 3. Test Results Summary
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| M1 PHY constraints | PASS | Unit/runtime documentation | Closed before this package; traceability retained |
| M2 RRC SIB1 RedCap | PASS | Unit/runtime documentation | Closed before this package; traceability retained |
| M3 BWP / CORESET / RA | PASS | Case A/B RFsim evidence | Runtime artifacts preserved for Case A and Case B |
| M4 SDT / RRC_INACTIVE | PASS | Unit/flow evidence | Closed before this package |
| M4-B DRX/eDRX/PSM | PASS | Unit/flow/runtime-boundary evidence | CN-driven PSM sleep not claimed |
| M5 mMTC scaling | PASS for accepted scope | 30/32/48/56 UE Case B pass; 64 UE classified | 56 UE accepted as sufficient simulation capacity |
| Report existence smoke check | PASS | Required reports / work daily logs | Required closure reports exist |
| Spec traceability review | PASS | `spec_traceability_matrix.md` | Uncertain clauses remain `[Needs Verification]` |

## 4. Evidence Map
| Milestone | Primary Evidence | Status |
|-----------|------------------|--------|
| M3 | `test_log/report/redcap_runtime_host_summary_case-a_disabled_2026-05-07_13-15-07.md` | PASS |
| M3 | `test_log/report/redcap_runtime_host_summary_case-b_disabled_2026-05-07_13-10-12.md` | PASS |
| M4-B | `test_log/report/m4b_lowpower_boundary_report_2026-05-07_13-25-44.md` | PASS |
| M5 30 UE | `test_log/report/m5_caseb_30ue_pass_report_2026-05-07_13-37-52.md` | PASS |
| M5 32 UE | `test_log/report/m5_rt_m5_032_caseb_pass_report_2026-05-08_10-14-38.md` | PASS |
| M5 48 UE | `test_log/report/m5_rt_m5_048_caseb_pass_report_2026-05-08_10-32-13.md` | PASS |
| M5 56 UE | `test_log/report/m5_rt_m5_056_caseb_static_cn_pass_report_2026-05-08_12-18-10.md` | PASS |
| M5 64 UE | `test_log/report/m5_rt_m5_064_caseb_static_cn_threshold_report_2026-05-08_17-14-00.md` | CLASSIFIED |

## 5. 3GPP Specification Mapping
| Flow | Clause | Mapping |
|------|--------|---------|
| RedCap PHY constraints | TS 38.101-1 Section 5.3; TS 38.306 Section 4 [Needs Verification] | M1 limits and antenna capability documentation |
| RedCap SIB1 / BWP | TS 38.331 Section 6.3.1 / 6.3.2 [Needs Verification] | M2/M3 RedCap RRC config and BWP behavior |
| Random Access | TS 38.321 Section 5.1 | M3/M5 Msg1-Msg4 flow validation |
| RAR reception | TS 38.321 Section 5.1.4 [Needs Verification] | M5 Msg2 window and RAR retry classification |
| Contention resolution | TS 38.321 Section 5.1.5 [Needs Verification] | M5 Msg4 ACK / CBRA completion counters |
| Connected DRX | TS 38.321 Section 5.7 | M4-B unit/flow-level boundary |
| eDRX / PSM | TS 38.331 Section 6.3.2; TS 24.501 Section 8.2.7.1.1 / 5.5.1 [Needs Verification] | M4-B low-power boundary documentation |

## 6. Practice Exercises
- [Basic] Why is [64 UE] kept as a classified upper-bound failure rather than a required pass criterion?
- [Applied] Which evidence files prove that [56 UE] is the accepted stable mMTC simulation point?
- [Advanced] How would you extend this package if a future run adds host resource telemetry for 64 UE?

## Closure Notes
- [M6] is closed as documentation/evidence packaging.
- No source code was changed for this package.
- No new clause numbers were invented; uncertain mappings remain marked `[Needs Verification]`.
