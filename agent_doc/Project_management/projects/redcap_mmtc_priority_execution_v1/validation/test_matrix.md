# RedCap mMTC Test Matrix

## Purpose
- Define reusable test IDs for milestone execution.
- Avoid repeating long test descriptions in every milestone file.
- Keep unit, flow, and runtime validation separate.

## Status Legend
- `[ ]`: Not started
- `[~]`: In progress
- `[x]`: Passed
- `[!]`: Blocked or failed
- `[NA]`: Not applicable

## Unit Tests
| Test ID | Milestone | Type | Command / Source | Pass Criteria | Status |
|---|---|---|---|---|---|
| UT-M1-001 | M1 | Unit | closest RedCap PRB helper CTest | Invalid PRB rejected, valid PRB accepted | [x] |
| UT-M1-002 | M1 | Unit | HD-FDD helper CTest | Tx/Rx gap guard deterministic | [x] |
| UT-M2-001 | M2 | Unit | RedCap SIB1 encode/decode test | ASN.1 encode/decode succeeds | [x] |
| UT-M2-002 | M2 | Unit | barring helper test | 1Rx barring gate matches config | [x] |
| UT-M3-001 | M3 | Unit | `ctest -R test_nr_redcap_bwp` | All RedCap BWP helper cases pass | [x] |
| UT-M3-002 | M3 | Unit | `ctest -R test_nr_redcap_coreset0` | Case A/B values parse correctly | [x] |
| UT-M3-003 | M3 | Unit | UE RA-RNTI BWP domain test | Nonzero CORESET uses current BWP | [x] |
| UT-M4-001 | M4 | Unit | SDT FSM MsgA test | Expected state sequence reached | [x] |
| UT-M4-002 | M4 | Unit | SDT FSM Msg3 fallback test | Fallback state sequence reached | [x] |
| UT-M4B-001 | M4-B | Unit | `ctest -R test_nr_ue_drx` | DRX config accepted without not-implemented path | [x] |
| UT-M4B-002 | M4-B | Unit | `ctest -R test_nr_rrc_lowpower` | eDRX fields round-trip | [x] |
| UT-M4B-003 | M4-B | Unit | `ctest -R test_nr_nas_lowpower` | Timer state tracked and logged | [x] |
| UT-M6-001 | M6 | Unit | report parser smoke test | Existing logs parsed without error | [~] |
| UT-M6-002 | M6 | Unit | doc link check | Project doc links resolve | [ ] |
| UT-M7-001 | M7 | Hygiene | `git diff --check` | No whitespace errors after cleanup | [ ] |
| UT-M7-002 | M7 | Hygiene | `bash -n <modified scripts>` | Modified shell scripts parse cleanly | [ ] |
| UT-M7-003 | M7 | Hygiene | `rg` reference scan | Removed files have no stale active references | [ ] |

## Flow Validations
| Test ID | Milestone | Flow | Log Source | Pass Criteria | Status |
|---|---|---|---|---|---|
| FV-M2-001 | M2 | SIB1 RedCap support | gNB/UE logs | UE reads RedCap support and barring fields | [x] |
| FV-M3-001 | M3 | RA Msg1 to Msg4 | gNB/UE logs | Msg1, RAR, Msg3, Msg4 complete | [x] |
| FV-M3-CASEB | M3 | Case B RA-RNTI monitoring | gNB/UE logs | gNB DCI and UE monitor both use BWP51 | [x] |
| FV-M5-RA-MSG4 | M5 | RA/Msg4 under load | gNB logs | RA window and Msg4 failures counted | [~] |
| FV-M4B-DRX | M4-B | Connected DRX runtime transition | UE/gNB logs | No DRX-configured RFsim scenario in current runtime set; covered by unit/flow helper | [NA] |
| FV-M4B-BOUNDARY | M4-B | DRX/eDRX/PSM boundary | Unit logs + RFsim logs | DRX unit/flow-level, eDRX/PSM runtime log-level, unsupported CN behavior not claimed | [x] |

## Runtime Validations
| Test ID | Milestone | Scenario | Command / Log Source | Pass Criteria | Status |
|---|---|---|---|---|---|
| RT-M3-CASEA | M3 | RFsim Case A | `redcap_runtime_host_validation.sh` | UE attach, RAR received, no LDPC failure | [x] |
| RT-M3-CASEB | M3 | RFsim Case B | `redcap_runtime_host_validation.sh` | UE attach, `coreset_id=1`, BWP51, no LDPC failure | [x] |
| RT-M3-UE2-RAR | M3 | UE2 RedCap RAR | UE2/gNB logs | UE2 receives RAR and proceeds beyond Msg2 | [x] |
| RT-M4B-001 | M4-B | Connected DRX runtime smoke | RFsim DRX-enabled config | No DRX-enabled runtime config in current source-of-truth compose path | [NA] |
| RT-M4B-002 | M4-B | eDRX/PSM log-level validation | Case A/B UE logs | eDRX SIB1 flags and NAS PSM timer logs visible; CN-driven PSM sleep not claimed | [x] |
| RT-M5-002 | M5 | fixed UE1/UE2 | RFsim compose logs | Attach, PDU session, tunnel, forward ping | [x] |
| RT-M5-030 | M5 | 30 UE staged | `redcap_mmtc_smoke_validation.sh` | 30/30 attach/PDU/tunnel/ping | [!] |
| RT-M5-CASEB-030 | M5 | 30 UE staged Case B | generated Case B gNB config + mMTC script | Compare Case A vs Case B failure counters | [x] |
| RT-M5-032 | M5 | 32 UE staged | mMTC logs | 32/32 attach/PDU/tunnel/ping | [ ] |
| RT-M5-064 | M5 | 64 UE staged | mMTC logs | result classified, blockers logged | [ ] |

## Reporting Rule
- Every completed validation must write or update a daily log under `test_logs/work_daily/`.
- Report these statuses separately:
  - [source build PASS/FAIL]
  - [unit test PASS/FAIL/NA]
  - [container image rebuilt or not]
  - [RFsim UE/gNB/CN runtime PASS/FAIL/NA]
