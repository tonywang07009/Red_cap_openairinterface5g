# M5 Case B 30 UE Runtime Report

## 1. Technical Background
- [mMTC staged scaling] stresses [Random Access], [RRC setup], [PDU session], tunnel creation, and parallel user-plane reachability.
- [Case B] keeps Msg2 scheduling inside the RedCap initial BWP/common CORESET path, reducing BWP-domain mismatch risk.
- This run evaluates whether the prior [RA/Msg4 contention] and [PUCCH common fallback] blockers still prevent 30 UE completion.

## 2. Key C Functions / Data Structures
- `gNB_scheduler_RA.c` — gNB RA Msg2/Msg4 scheduling and runtime markers.
- `nr_mac_redcap_bwp.c` — RedCap Case A/B BWP and CORESET helper path.
- `nr_ue_procedures.c` — UE RA-RNTI monitoring and Msg2 handling path.
- `ci-scripts/redcap_mmtc_smoke_validation.sh` — staged UE launch, tunnel, ping, and log capture.

## 3. Test Results Summary Table
| Test Item | Pass-Fail Status | Code Coverage | Modification Logs |
|-----------|------------------|---------------|-------------------|
| [RT-M5-CASEB-030] | PASS | 30 UE staged attach/PDU/tun/parallel ping | `test_log/compiler_logs/mmtc_smoke_30ue_caseb_rerun_2026-05-07_13-29-43_escalated.log` |
| gNB restart gate | PASS | gNB restart count stayed `0` | `test_log/compiler_logs/mmtc_smoke_2026-05-07_13-29-43_gnb_state.log` |
| Msg2 Case B path | PASS | `[gNB Msg2 DCI]=30`, `30 x cce=0 agg=4` | `test_log/compiler_logs/mmtc_smoke_2026-05-07_13-29-43_gnb.log` |
| Msg4 contention path | PASS | Msg4 ACK / CBRA success `30`, contention timer `0` | Same gNB log |
| UE PUCCH fallback blocker | PASS | `pucch_ResourceCommon is NULL=0` | UE docker logs under `test_log/compiler_logs/` |

## 4. 3GPP Specification Mapping
- TS 38.321 Section 5.1 — Random Access procedure.
- TS 38.321 Section 5.1.4 — RAR/Msg2 reception and RA response window. Exact subsection: [Needs Verification].
- TS 38.321 Section 5.1.5 — contention resolution / Msg4 behavior. Exact subsection: [Needs Verification].
- TS 38.331 Section 6.3.2 — RedCap initial BWP / common configuration context. Exact subsection: [Needs Verification].
- TS 38.213 Section 13 — Type0/common search space and CORESET behavior. Exact subsection: [Needs Verification].

## 5. Practice Exercises
- Basic: Explain why a UE can show transient [RAR reception failed] and still pass final attach/PDU/tunnel validation.
- Applied: Compare `[gNB Msg2 gate]` and `[gNB Msg2 DCI]`; explain why gate count can exceed successful DCI count under RA retries.
- Advanced: Design the next 32 UE validation so it separates [capacity threshold] from [scheduler regression].
