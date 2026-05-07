# Work Daily Log
## Session Metadata
- Date: 2026-05-06 20:37
- Agent Session ID: N/A
- Task Slug: rt-m5-032-caseb-pucch-fallback-validation
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md
- Milestone File: milestones/M5_mmtc_runtime_scaling.md
- Validation File: validation/test_matrix.md / validation/runtime_checklist.md
- Task ID: M5-T2 / M5-T3
- Batch: B

## Milestone & Sub-task Reference
- Milestone: M5 mMTC Runtime Scaling
- Sub-task: RT-M5-032 32 UE staged Case B validation after PUCCH fallback root fix
- Status: [COMPLETED]

## What Was Done
- Ran `RT-M5-032` using the same stable runtime profile as the passing 30 UE Case B baseline:
  - `GNB_REDCAP_CONFIG=test_log/runtime_configs/gnb.redcap_mmtc_case-b_2026-05-02_12-35-01.yaml`
  - `MMTC_TOTAL_UES=50`
  - `MMTC_SAMPLE_UES=1..32`
  - `MMTC_CN_COMPOSE=/home/tonywang/OAI/oai-cn5g/docker-compose.yaml`
  - `MMTC_USE_EXISTING_CN_DB=1`
  - `MMTC_RESET_CN=1`
  - `MMTC_UE_START_GAP=8`
  - `MMTC_FORWARD_PING_MODE=parallel`
  - `MMTC_RUN_REVERSE_PING=0`
  - `MMTC_IPERF_ENABLE=0`
- Confirmed smoke script header:
  - `[INFO] UE PUCCH fallback : bwp0_common=1`
- Confirmed no recovery was needed:
  - `Recovery restarted 0 sampled UE container(s)`
  - `gNB restart count : 0`
- Confirmed UE31/UE32 runtime:
  - both containers had `MMTC_PUCCH_COMMON_FALLBACK_BWP0=1`
  - both reached `Interface oaitun_ue1 successfully configured`
  - both used `[CGDBG][PUCCH-FALLBACK] use BWP0 common resource`

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1.4 [Needs Verification] - RAR reception and RA response window.
- TS 38.321 Section 5.1.5 [Needs Verification] - contention resolution / Msg4 completion.
- TS 38.213 Section 9.2.1 [Needs Verification] - initial PUCCH resource before dedicated PUCCH configuration.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Source build | N/A | Runtime-only validation | No C/C++ file changed for this run. |
| Unit test | N/A | Runtime-only validation | Closest validation is RFsim Docker run. |
| Container image rebuilt | N/A | Existing local images | Shell/runtime validation reused current local images. |
| RT-M5-032 RFsim runtime | PASS | 32 sampled UEs | `sample=32 running=32 attach=32 pdu=32 tun=32 forward_ping_ok=32 gnb_restart=0 failures=0`. |
| UE31/UE32 fallback path | PASS | UE runtime logs | `PUCCH_NULL=0`; `FALLBACK_USE=1`; both reached tunnel. |
| RA/Msg4 counters | PASS | gNB runtime log | Msg4 `vrb_map=0`, contention timer `0`, Msg4 fail `0`; Msg2 window fail `6`. |

## Counter Summary
| Counter | RT-M5-032 Result | Notes |
|---------|------------------|-------|
| Attach/PDU/TUN/ping | 32/32 | Parallel forward ping passed for all sampled UEs. |
| gNB restart | 0 | No RAN container restart. |
| Recovery restarted UEs | 0 | No sampled UE needed restart. |
| Msg2 window fail | 6 | Low residual RA window misses; did not block completion. |
| RA CCE allocation fail | 0 | Exact RA CCE allocation marker absent. |
| Msg2 vrb_map fail | 0 | No RA Msg2 VRB allocation failure marker. |
| Msg4 vrb_map fail | 0 | No Msg4 allocation failure marker. |
| Msg4 contention timer expired | 0 | No contention-resolution storm. |
| RA Procedure failed at Msg4 | 0 | Msg4 path recovered after fallback fix. |
| Msg4 compact alloc | 56 | Compact-first Msg4 allocation active. |

## Known Issues / Blockers
- No blocker remains for `RT-M5-032` under the current Case B + fallback profile.
- Residual Msg2 window misses still appear at low count (`6`), so `RT-M5-064` should continue tracking whether RA response window or Msg2 scheduling priority needs tuning under larger load.
- The PUCCH fallback remains a runtime mitigation pending a spec-clean review of whether BWP1 should carry common PUCCH config or whether initial PUCCH ACK should be anchored differently.

## Next Step
- Run `RT-M5-064` or a staged 50/64 UE scan with the same Case B and PUCCH fallback baseline, then compare Msg2 window, Msg2 CCE, Msg4 vrb_map, and contention timer counters.
