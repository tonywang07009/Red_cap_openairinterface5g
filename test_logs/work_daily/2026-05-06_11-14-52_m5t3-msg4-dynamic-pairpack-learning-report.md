# Educational Learning Report

## 1. Technical Background
- [RedCap mMTC RA] stress appears when many UEs enter random access with a narrow effective BWP and limited control resources.
- [Msg2] needs to satisfy the random access response window; when scheduling is delayed, the gNB logs `[Msg2 window fail]`.
- [Msg4] carries contention resolution and RRC setup data. In this scenario, compact low-MCS Msg4 needs about 25 PRBs, so two Msg4 PDUs do not fit cleanly in a 48 PRB BWP.
- The tested scheduler strategy now tries low-MCS `[compact alloc]` first, then uses `[pair-pack alloc]` only when compact allocation cannot fit in the current slot.
- Latest runtime showed improved RA resource counters, but end-to-end PDU/TUN validation was blocked by CN-side `[UPF selection failed]`.

## 2. Key C Functions / Data Structures
- `nr_schedule_RA()` — splits RA scheduling into timer handling, Msg2, Msg3 retransmission, and Msg4/MsgB passes.
- `nr_generate_Msg4_MsgB()` — builds and schedules Msg4/MsgB DCI/PDSCH/PUCCH feedback.
- `find_compact_ra_pdsch_allocation()` — finds low-MCS compact Msg4 PDSCH allocation.
- `find_bounded_ra_pdsch_allocation()` — finds allocation constrained by a PRB cap for pair packing.
- `find_free_ra_pdsch_rb_start()` — checks whether a candidate Msg4 allocation has contiguous PRB space in the slot VRB map.
- `NR_RA_t`, `NR_UE_sched_ctrl_t`, `ra_pdsch_allocation_t`, `bwp_info_t`.

## 3. Test Results Summary Table
| Test Item | Status | Coverage | Notes |
|-----------|--------|----------|-------|
| `nr-softmodem` build | PASS | gNB MAC scheduler | dynamic pair-pack patch compiled |
| `test_nr_redcap_bwp` | PASS | RedCap BWP regression | LSAN disabled |
| image rebuild | PASS | Docker runtime images | marker verified |
| RT-M5-CASEB-030 | FAIL/BLOCKED | 30 sampled UE RFsim | CN-side UPF selection failed |

## 4. 3GPP Specification Mapping
- TS 38.321 Section 5.1.4 — [Random Access Response] timing window pressure. [Needs Verification]
- TS 38.321 Section 5.1.5 — [Contention Resolution] and Msg4 success/failure behavior. [Needs Verification]
- TS 38.306 Section 4.2 — [UE radio access capability] baseline for RedCap reduced capability handling. [Needs Verification]

## 5. Practice Exercises
- Basic: Explain why a 25 PRB Msg4 allocation cannot pair-pack two UEs inside a 48 PRB BWP.
- Applied: Given `Msg2 window fail=44` and `Msg4 vrb_map fail=4`, identify which RA bottleneck improved and which remains unresolved.
- Advanced: Propose a scheduler rule that balances low MCS reliability with PRB packing under high RedCap RA load, and define two counters to validate it.
