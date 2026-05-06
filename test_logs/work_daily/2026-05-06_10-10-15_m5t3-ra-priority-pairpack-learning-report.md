# M5-T3 RA Priority Pair-Pack Learning Report

## 1. Technical Background
- [RedCap mMTC RFsim] creates many near-simultaneous RA attempts.
- Under this load, [Msg2] is time-critical because it must fit inside the configured [RA response window].
- The previous runtime logs showed many [Msg4] allocations using `rb_size=25` in a `48 PRB` BWP.
- That pattern leaves only `23 PRBs`, so a second Msg4 in the same slot cannot fit even though almost half the BWP is still free.
- This patch reduces that pressure by trying a [pair-pack] Msg4 allocation first and by scheduling all [Msg2] attempts before [Msg4].
- The RA state machine is not changed; only local scheduler ordering and PDSCH PRB/MCS choice are adjusted.

## 2. Key C Functions / Data Structures
- `find_bounded_ra_pdsch_allocation()` — searches for a bounded PRB allocation using ascending MCS and PRB count.
- `find_compact_ra_pdsch_allocation()` — existing RedCap compact allocation fallback.
- `nr_generate_Msg4_MsgB()` — schedules Msg4/MsgB PDCCH, PDSCH, HARQ feedback, and TX request.
- `nr_generate_Msg2()` — schedules RAR/Msg2 and Msg3 allocation.
- `nr_schedule_RA()` — now prioritizes Msg2, then Msg3 retransmission, then Msg4/MsgB.
- `ra_pdsch_allocation_t` — carries selected `rb_size`, `mcs`, `R`, `Qm`, and `tb_size`.

## 3. Test Results Summary Table
| Test Item | Status | Coverage | Notes |
|---|---|---|---|
| `nr-softmodem` build | PASS | gNB MAC RA scheduler compile/link | `build_nr-softmodem_2026-05-06_10-09-02_m5t3-ra-priority-pairpack.log` |
| `test_nr_redcap_bwp` | PASS | RedCap BWP/RA helper regression | `ctest_test_nr_redcap_bwp_2026-05-06_10-09-11_m5t3-ra-priority-pairpack-lsanoff.log` |
| Local image rebuild | FAIL | Docker runtime packaging | Docker socket permission denied |
| `RT-M5-CASEB-030` | NOT RUN | 30 UE Case B runtime | Blocked until image rebuild succeeds |

## 4. 3GPP Specification Mapping
- TS 38.321 Section 5.1 — maps to the four-step RA flow [Msg1/RAR/Msg3/Msg4].
- TS 38.321 Section 5.1.4 — maps to [RAR reception window]; exact wording [Needs Verification].
- TS 38.321 Section 5.1.5 — maps to [contention resolution] and Msg4 ACK/NACK handling.
- TS 38.214 Section 5.1.2.2 — maps to [PDSCH resource allocation] for PRB/MCS/TBS selection; exact detail [Needs Verification].
- TS 38.306 Section 4 — maps to [RedCap bandwidth/capability constraints]; exact subsection [Needs Verification].

## 5. Practice Exercises
- Basic: Explain why `rb_size=25` is inefficient in a `48 PRB` RedCap BWP under multi-UE RA load.
- Applied: Given `BWP=48`, design a scheduler rule that allows two Msg4 PDUs to fit in one slot while limiting MCS increase.
- Advanced: Compare two approaches for reducing Msg2 window failures: [prioritizing Msg2 scheduling order] versus [increasing RA response window]. Which one better preserves OAI's current 10 ms guard, and why?
