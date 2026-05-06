# Work Daily Log
## Session Metadata
- Date: 2026-05-06 11:14
- Agent Session ID: N/A
- Task Slug: m5t3-msg4-dynamic-pairpack-runtime
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: M5 mMTC Runtime Scaling
- Sub-task: M5-T3 / RT-M5-CASEB-030 RedCap RA Msg2/Msg4 congestion validation
- Status: IN-PROGRESS

## What Was Done
- Rebuilt local Docker runtime images with Docker permission.
- Verified `oai-gnb:latest` binary marker: `[RedCap RA][gNB %s pair-pack alloc]`.
- Ran RT-M5-CASEB-030 with `MMTC_TOTAL_UES=50`, sampled `UE1..UE30`, `MMTC_UE_START_GAP=8`, parallel forward ping, reverse ping disabled, iperf disabled.
- Tested three Msg4 allocation variants:
  - pair-pack max MCS 6: `attach=9`, `pdu=9`, `tun=9`, `forward_ping_ok=9`.
  - MCS4-only compact: `attach=11`, `pdu=10`, `tun=10`, `forward_ping_ok=10`.
  - dynamic compact-first pair-pack: `attach=6`, `pdu=0`, `tun=0`, `forward_ping_ok=0`, but CN/SMF showed repeated `[UPF selection failed]`.
- Updated `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c`:
  - Added `find_free_ra_pdsch_rb_start()`.
  - Changed RedCap Msg4 allocation to prefer compact MCS4 when slot PRBs fit, and use pair-pack only when compact has no contiguous PRB window.

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1.5 — Random Access Contention Resolution / Msg4 behavior. [Needs Verification]
- TS 38.321 Section 5.1.4 — Random Access Response / Msg2 timing pressure. [Needs Verification]
- TS 38.306 Section 4.2 — UE radio access capability framework relevant to RedCap reduced capability assumptions. [Needs Verification]

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| source build: `nr-softmodem` | PASS | gNB MAC scheduler compile/link | `build_nr-softmodem_2026-05-06_*_m5t3-msg4-dynamic-pairpack.log` |
| unit test: `test_nr_redcap_bwp` | PASS | closest RedCap BWP regression | LSAN disabled: `detect_leaks=0` |
| container image rebuild | PASS | `ran-build`, `oai-gnb`, `oai-nr-ue` | image marker includes `rb_start` field |
| RT-M5-CASEB-030 pair-pack max MCS 6 | FAIL | 30 sampled UE runtime | summary `attach=9 pdu=9 tun=9 forward_ping_ok=9` |
| RT-M5-CASEB-030 MCS4 compact | FAIL | 30 sampled UE runtime | summary `attach=11 pdu=10 tun=10 forward_ping_ok=10` |
| RT-M5-CASEB-030 dynamic compact-first | FAIL / BLOCKED | 30 sampled UE runtime | summary `attach=6 pdu=0 tun=0`; SMF `UPF selection failed` x6 |

## Counter Comparison
| Counter | pair-pack max MCS6 | MCS4 compact | dynamic compact-first |
|---------|--------------------|--------------|-----------------------|
| Msg2 window fail | 130 | 174 | 44 |
| Msg2 CCE fail | 17 | 32 | 16 |
| Msg4 vrb_map fail | 0 | 24 | 4 |
| Received Nack in Msg4 | 852 | 1139 | 930 |
| RA Procedure failed at Msg4 | 284 | 379 | 310 |
| RA contention timer expired | 284 | 379 | 310 |
| pair-pack alloc | 3826 | 0 | 50 |
| compact alloc | 0 | 5191 | 4100 |

## Known Issues / Blockers
- Dynamic compact-first reduces Msg2 and Msg4 resource counters, but latest end-to-end result is blocked by CN-side `[SMF UPF selection failed]`, not conclusively by gNB RA.
- The CN/UPF issue must be resolved or the runtime rerun with a clean/healthy CN before judging dynamic pair-pack endpoint success.
- Msg4 HARQ NACK/contention remains high across all variants.

## Next Step
- First verify CN/UPF health and why SMF cannot select UPF, then rerun RT-M5-CASEB-030 with the dynamic compact-first patch.
- If CN is healthy and runtime still fails, inspect Msg4 ACK/NACK scheduling and PUCCH feedback resources for RedCap RA contention.
