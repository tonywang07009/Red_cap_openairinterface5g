# RT-M5-056 Case B Threshold Report

## Technical Background
- [RT-M5-056] extends the Case B staged mMTC runtime baseline from 48 to 56 sampled UEs.
- The purpose is to separate [RAN RA/Msg4 pressure] from [CN/NAS/PDU pressure] before deciding whether 60/64 UE tests should be treated as scheduler work or core-network scaling work.
- Case B keeps RedCap Msg2 in the common CORESET/BWP path validated by M3, while `MMTC_PUCCH_COMMON_FALLBACK_BWP0=1` keeps the UE-side PUCCH common fallback enabled.
- This run is a threshold classification, not a source patch validation.

## Key Runtime Components
- Script: `ci-scripts/redcap_mmtc_smoke_validation.sh`.
- Scenario: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`.
- gNB config: `test_log/runtime_configs/gnb.redcap_mmtc_case-b_2026-05-02_12-35-01.yaml`.
- Main log: `test_log/compiler_logs/mmtc_smoke_56ue_caseb_2026-05-08_11-20-59_escalated.log`.
- Preserved artifacts: `test_log/runtime_artifacts/m5_rt_m5_056_caseb_2026-05-08_11-20-59/`.

## Test Results Summary
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| RT-M5-056 | FAIL / classified | `56` running, `54` attach, `53` PDU/tunnel/ping | failure count `3` |
| gNB restart gate | PASS | restart count `0` | no gNB crash/restart |
| Msg2 Case B path | PASS | gate `440`, DCI `56`, CCE `56 x cce=0 agg=4` | all sampled UEs received Msg2 DCI allocation evidence |
| Msg2 failure counters | PASS with pressure | window fail `25`, vrb_map fail `0`, UE RAR reception failed `25`, LDPC fail `0` | retry pressure increased but was not terminal |
| Msg4 contention path | PASS | Msg4 vrb_map fail `0`, contention timer expired `0`, Msg4 ACK / CBRA success `56` | contention-resolution blocker not reproduced |
| UE PUCCH fallback blocker | PASS | `pucch_ResourceCommon is NULL=0`, `fallback=0/1=0` | fallback env enabled |
| CN/NAS/PDU late path | FAIL | UE54/55/56 no `oaitun_ue1` | UE54/55 Registration Reject; UE56 SMF selection failure |
| Ping latency | PASS with pressure | `53/53` available ping logs show `0% packet loss` | avg-of-avg `787.689 ms`, max-max `2039.815 ms` |
| Source build | N/A | no C/C++ source patch | existing local images used |
| Unit test | N/A | pure runtime validation | nearest validation is RFsim runtime |
| Container image rebuild | N/A | no source patch | existing local images used |

## Failure Localization
- [UE54] reached `NR_RRCSetup` and `RRCSetupComplete`, then received `FGS_REGISTRATION_REJECT`; AMF logged `Request Authentication Vectors failure`.
- [UE55] reached `NR_RRCSetup` and `RRCSetupComplete`, then received `FGS_REGISTRATION_REJECT`; AMF logged `Request Authentication Vectors failure`.
- [UE56] had five transient `RAR reception failed` retries, then reached `Registration Accept` and sent `PduSessionEstablishRequest`; AMF registered the UE but logged `SMF Selection, no SMF candidate is available`.
- [Interpretation] RAN RA/Msg4 stayed clean at 56 UE; the first threshold failure is [CN/NAS/PDU late-stage pressure].

## 3GPP Specification Mapping
| Clause | Mapping |
|--------|---------|
| TS 38.321 Section 5.1 | Random Access procedure baseline for Msg1-Msg4. |
| TS 38.321 Section 5.1.4 | RAR / Msg2 response-window behavior. Exact subsection: [Needs Verification]. |
| TS 38.321 Section 5.1.5 | Contention resolution / Msg4 behavior. Exact subsection: [Needs Verification]. |
| TS 38.331 Section 6.3.2 | RedCap initial BWP/common configuration context. Exact subsection: [Needs Verification]. |
| TS 38.213 Section 13 | Common search space / CORESET behavior for Msg2 monitoring. Exact subsection: [Needs Verification]. |
| TS 24.501 registration and PDU session clauses | NAS Registration Reject and PDU session establishment path. Exact clauses: [Needs Verification]. |

## Practice Exercises
- Basic: Explain why `Msg4 ACK / CBRA success=56` means this failure should not be classified as contention-resolution failure.
- Applied: Compare the 48 UE and 56 UE Msg2 window-fail counters and decide whether RAR window tuning alone would solve UE54/55/56.
- Advanced: Design a follow-up run that separates AMF authentication-vector pressure from NRF/SMF discovery pressure without changing gNB scheduler code.
