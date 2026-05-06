# Work Daily Log
## Session Metadata
- Date: 2026-05-06 20:26
- Agent Session ID: N/A
- Task Slug: rt-m5-caseb-030-pucch-fallback-rootfix
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md
- Milestone File: milestones/M5_mmtc_runtime_scaling.md
- Validation File: validation/test_matrix.md / validation/runtime_checklist.md
- Task ID: M5-T3
- Batch: B

## Milestone & Sub-task Reference
- Milestone: M5 mMTC Runtime Scaling
- Sub-task: RCA and fix for UE23/UE29/UE30 Msg4 ACK PUCCH common fallback path
- Status: [COMPLETED]

## What Was Done
- Compared successful UE1 against failed UE23/UE29/UE30 from `RT-M5-CASEB-030` after the CN/UPF fix.
- Confirmed failed UE path:
  - RRCSetup was received.
  - UE switched to BWP1 after CellGroupConfig.
  - Msg4 ACK attempted initial PUCCH while BWP1 `pucch_ResourceCommon` was NULL.
  - Runtime marker showed `fallback=0`.
- Confirmed container env before fix:
  - UE1/UE23/UE29/UE30 all had `MMTC_PUCCH_COMMON_FALLBACK_BWP0=0`.
- Updated `ci-scripts/redcap_mmtc_smoke_validation.sh`:
  - default `MMTC_PUCCH_COMMON_FALLBACK_BWP0` to `1` for direct smoke validation,
  - export it so `docker compose` interpolates the generated mMTC overlay correctly,
  - print `[INFO] UE PUCCH fallback : bwp0_common=<value>` in the runtime header.

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1.4 [Needs Verification] - RAR reception timing and RA response window behavior.
- TS 38.321 Section 5.1.5 [Needs Verification] - contention resolution / Msg4 completion.
- TS 38.213 Section 9.2.1 [Needs Verification] - initial PUCCH resource before dedicated PUCCH configuration.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Root-cause comparison | PASS | UE1 vs UE23/UE29/UE30 logs | Failed UEs had BWP1 initial PUCCH NULL with `fallback=0`; successful UE completed PDU/tunnel. |
| Shell syntax | PASS | Modified smoke script | `bash -n ci-scripts/redcap_mmtc_smoke_validation.sh`. |
| Prepare-only smoke header | PASS | Script default/export path | Header printed `UE PUCCH fallback : bwp0_common=1`. |
| Source build | N/A | Shell-only change | No C/C++ file changed. |
| Unit test | N/A | Shell-only runtime fix | Closest validation is RFsim runtime. |
| Container image rebuilt | N/A | Shell-only change | Existing local images reused. |
| RT-M5-CASEB-030 RFsim runtime | PASS | 30 sampled UEs | `sample=30 running=30 attach=30 pdu=30 tun=30 forward_ping_ok=30 gnb_restart=0 failures=0`. |
| UE23/UE29/UE30 PUCCH fallback | PASS | UE runtime logs | New run shows `PUCCH-FALLBACK use BWP0 common resource`; `PUCCH_NULL=0`; all three have `oaitun_ue1`. |
| RA/Msg4 counters | PASS | gNB runtime log | Msg4 `vrb_map=0`, contention timer `0`, Msg4 fail `0`; Msg2 window fail reduced `298 -> 8`. |

## Counter Comparison
| Counter | Before Fix | After Fix | Notes |
|---------|------------|-----------|-------|
| Attach/PDU/TUN/ping | 27/30 | 30/30 | UE23/UE29/UE30 recovered. |
| Msg2 window fail | 298 | 8 | Remaining low count did not block 30 UE pass. |
| RA CCE allocation fail | 82 | 0 | Counted exact RA CCE allocation marker; broad periodic UE `CCE fail` stats are noisy. |
| Msg4 vrb_map fail | 4 | 0 | Dynamic compact Msg4 allocation remains sufficient for this run. |
| Msg4 contention timer expired | 376 | 0 | Confirms prior contention storm was tied to missed Msg4 ACK path. |
| RA Procedure failed at Msg4 | 376 | 0 | Cleared after fallback enable. |
| UE23 PUCCH NULL / fallback use | 18 / 0 | 0 / 1 | UE23 now reaches PDU/tunnel. |
| UE29 PUCCH NULL / fallback use | 8 / 0 | 0 / 1 | UE29 had 2 RAR misses but recovered. |
| UE30 PUCCH NULL / fallback use | 7 / 0 | 0 / 1 | UE30 now reaches PDU/tunnel. |

## Known Issues / Blockers
- No blocker remains for `RT-M5-CASEB-030` at 30 sampled UEs.
- Msg2 window misses still exist at low count (`8`), so larger 32/64 UE staged runs should still monitor RA window pressure.
- The fallback is an mMTC validation mitigation. A spec-clean long-term fix should verify whether BWP1 should carry a valid common PUCCH config or whether initial PUCCH should remain anchored to the proper common UL BWP.

## Next Step
- Run `RT-M5-032` or the next staged scan with the same fallback default to determine whether RAR response window or Msg2 scheduling priority still needs adjustment beyond 30 UE Case B.
