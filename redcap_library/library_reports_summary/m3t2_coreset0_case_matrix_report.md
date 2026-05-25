# M3-T2 CORESET#0 Case A/B Runtime Evidence Report

## Technical Background
- [M3-T2] targets [RedCap CORESET#0 Case A/B] runtime evidence for [TS 38.331 SIB1 RedCap initial BWP] behavior.
- [Case A] keeps [type0 CSS] behavior and should support full attach, PDU session, ping, and UL iperf.
- [Case B] uses an [edge-aligned commonControlResourceSet] for the RedCap initial DL BWP. In this run, gNB and UE both showed RedCap BWP application, but UE2 failed during [RAR reception].
- [TS 38.321 Section 5.1] maps this failure to [Random Access] before [RRCSetupComplete], not NAS Registration or PDU Session establishment.

## Key C Functions / Data Structures
- [openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c]
  - [apply_redcap_case_b_common_coreset] builds Case B [commonControlResourceSet].
  - [clone_redcap_downlink_bwp] / [clone_redcap_uplink_bwp] clone RedCap initial BWP common configs into SIB1.
- [openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c]
  - [nr_generate_Msg2] schedules [RA-Msg2 DCI] on [RA-RNTI].
  - [prepare_dl_pdus] creates PDCCH/PDSCH PDUs for Msg2.
- [openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c]
  - [nr_rar_not_successful] handles [RAR reception failed].

## Test Results Summary
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| [Case A 2-UE RFsim host runtime] | PASS | UE1 attach, UE2 RedCap attach, PDU, ping, iperf 50/20 Mbps | Summary: `test_log/report/redcap_runtime_host_summary_case-a_disabled_2026-04-29_11-42-14.md` |
| [Case A CORESET#0 marker] | PASS | gNB log marker | `RedCap CORESET#0 Case A type0 CSS` |
| [Case B CORESET#0 marker] | PASS | gNB log marker | `RedCap CORESET#0 Case B edge-aligned PRB allocation: start=0 size=51 carrier_bw=106 common_coreset_id=1` |
| [Case B UE RedCap BWP apply] | PASS | UE2 log marker | UE2 applied RedCap initial DL/UL BWP repeatedly |
| [Case B UE2 attach/PDU/ping] | FAIL | Runtime RA path | UE2 repeatedly logs `RAR reception failed`; gNB generates Msg2 but reaches `WAIT_Msg3` failure |
| [test_nr_redcap_coreset0 build] | PASS | Unit-test target build | `ninja: no work to do` |
| [test_nr_redcap_coreset0 CTest] | PASS | 13 GoogleTest cases | Passed with `LSAN_OPTIONS=detect_leaks=0`; default CTest failed only due [LeakSanitizer under ptrace] |

## 3GPP Specification Mapping
- [TS 38.306 Clause 4.2.21.1] — RedCap bandwidth and capability constraints relevant to [20 MHz / 51 PRB] initial BWP.
- [TS 38.331 Clause 5.2.2.4.2] — SIB1 acquisition and serving-cell common configuration delivery.
- [TS 38.331 Clause 5.6.1.3] — Bandwidth part configuration behavior.
- [TS 38.321 Section 5.1] — Random Access procedure; current Case B failure occurs before Msg3/RRC completion.

## Modification / Evidence Notes
- [Modification Point] → [No C/C++ code changed in this sub-task]
- [Reason] → [This step collected runtime evidence and isolated the failure stage]
- [Before vs. After Comparison] → [Before: Case A/B runtime status unclear after M4B work] / [After: Case A full PASS; Case B CORESET/SIB1 PASS but RA/RAR blocked]
- [Discussion Point] → [Next patch should focus on Case B Msg2/PDCCH monitoring or RA-RNTI scheduling under edge-aligned CORESET]

## Practice Exercises
- [Basic] Explain why [UE2 applying SIB1 RedCap initial DL/UL BWP] proves SIB1 decode but does not prove full attach.
- [Applied] Trace [nr_generate_Msg2] to [nr_rar_not_successful] and identify which logs confirm the failure is before [RRCSetupComplete].
- [Advanced] Propose a debug patch that logs [PDCCH CORESET/BWPStart/BWPSize/FreqDomainResource] for RA-Msg2 only, without flooding normal scheduling logs.

## Artifacts
- [Runtime matrix log] `test_log/compiler_logs/redcap_runtime_matrix_2026-04-29_11-42-14.log`
- [Case A host log] `test_log/compiler_logs/redcap_runtime_host_case-a_disabled_2026-04-29_11-42-14.log`
- [Case B host log] `test_log/compiler_logs/redcap_runtime_host_case-b_disabled_2026-04-29_11-46-23.log`
- [Case A summary] `test_log/report/redcap_runtime_host_summary_case-a_disabled_2026-04-29_11-42-14.md`
- [Case B summary] `test_log/report/redcap_runtime_host_summary_case-b_disabled_2026-04-29_11-46-23.md`
- [Unit test log] `test_log/compiler_logs/ctest_test_nr_redcap_coreset0_2026-04-29_11-57-54_m3t2_lsanoff.log`
