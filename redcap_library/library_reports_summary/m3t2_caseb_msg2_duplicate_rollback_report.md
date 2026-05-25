# M3-T2 Case B Msg2 Duplicate Rollback Report

## Scope
- [Milestone]：[M3-T2 CORESET#0 Case B RA/RAR bottleneck]
- [Focus]：Rollback unsafe [Msg2 DCI duplicate] behavior and re-validate mixed UE runtime.
- [Spec Mapping]：
  - [TS 38.331 Clause 5.2.2.4.2] — SIB1 acquisition and common configuration handling.
  - [TS 38.331 Clause 5.3.5] — RRCSetup / UE capability path after successful RA.
  - [TS 38.321 Clause 5.1] — 4-step Random Access procedure.

## Modification Points
- [Modification Point] → [gNB Msg2 duplicate DCI rollback]
- [Reason] → gNB cannot reliably distinguish [normal UE] and [RedCap UE] before Msg3 / UE capability; sending duplicate RA DCI on [coreset_id=1] polluted UE1 baseline RA.
- [Before vs. After Comparison] → Before: gNB emitted `[RedCap RA][gNB Msg2 DCI duplicate]`; After: only legacy `[RedCap RA][gNB Msg2 DCI]` diagnostic remains.
- [Discussion Point] → Case B needs a safer design than unconditional duplicate PDCCH for all RA-RNTI traffic.

## Build And Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| nr-softmodem build | PASS | gNB C patch | `build_nr-softmodem_*_m3t2-remove-msg2-dup.log` |
| test_nr_redcap_bwp build | PASS | BWP/CORESET helper | `ninja: no work to do` |
| test_nr_redcap_bwp CTest | PASS | 10 tests | First run hit [LeakSanitizer under ptrace]; rerun with `LSAN_OPTIONS=detect_leaks=0` passed |
| local OAI images rebuild | PASS | gNB/UE runtime images | `rebuild_local_oai_images_*_m3t2-remove-msg2-dup.log` |
| 2-UE RFsim Case B runtime | FAIL | UE1/UE2 attach/PDU/ping | UE1 attach/PDU PASS; UE2 RedCap attach FAIL |

## Runtime Findings
- [UE1 baseline restored]：
  - [Attach UE1] `333331`：[OK], IP `10.0.0.2`.
  - [Verify UE1 non-RedCap] `302001`：[OK].
- [UE2 Case B remaining failure]：
  - [Attach UE2 RedCap] `333332`：[KO].
  - UE2 applies [SIB1 RedCap initial DL/UL BWP] with `start=0 size=51`.
  - UE2 monitors [RA DCI] on `coreset_id=1`, `BWPSize=51`.
  - gNB still sends [Msg2 DCI] on `coreset_id=0`, `BWPSize=48`.
  - UE2 logs repeated `RAR reception failed`; gNB logs repeated `RA failed at state WAIT_Msg3`.
- [No duplicate pollution]：
  - No `[RedCap RA][gNB Msg2 DCI duplicate]` marker remains in the latest runtime path.

## Known Issues / Blockers
- [BLOCKED] Case B RedCap UE2 still cannot attach because the [RA Msg2 DCI search-space/BWP] path remains mismatched.
- [Needs Design] A safe Case B fix must avoid breaking normal UE RA. Candidate direction: infer RedCap RA from an explicit RA resource partition or configure RedCap-specific RA path before Msg2; unconditional duplicate DCI is not acceptable.

## Next Step
- Continue [M3-T2] with a safe [Case B RedCap RA Msg2] design that preserves UE1 baseline and targets UE2 [coreset_id=1 / BWP51] without global RA-RNTI duplication.
