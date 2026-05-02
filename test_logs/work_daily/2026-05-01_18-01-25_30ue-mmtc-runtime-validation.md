# Work Daily Log
## Session Metadata
- Date: 2026-05-01 18:01
- Agent Session ID: N/A
- Task Slug: 30ue-mmtc-runtime-validation
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: M5 - Compose Architecture, Integration & UL Throughput
- Sub-task: 30 UE mMTC runtime access validation
- Status: [BLOCKED]

## What Was Done
- Checked the fixed RedCap compose path and confirmed the base `docker-compose.yml` defines UE1..UE28.
- Confirmed `docker-compose.mmtc.yml` provides scalable UE29+ overlay and `generate_mmtc_cn_db_overlay.sh` generates CN subscribers beyond the baseline UE1..UE4 database.
- Ran 30 UE smoke validation with UE1..UE30 selected.
- First run used 2s UE start gap: 6/30 attach, PDU, TUN, and ping passed; 24/30 failed before TUN.
- Second run used 8s UE start gap: 26/30 attach, PDU, TUN, and ping passed; UE11, UE20, UE26, UE29 failed before TUN.
- Confirmed gNB restart count stayed 0 in both runs.
- Confirmed LDPC decode failure did not appear in the failed UE logs; the failure shifted to RA/Msg4 resource/timing behavior under load.

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1 - Random Access procedure; relevant to Msg1/Msg2/Msg3/Msg4 behavior and contention resolution.
- TS 38.331 Section 6.3.2 - RedCap initial DL/UL BWP configuration; relevant to RedCap SIB1 BWP behavior.
- TS 38.306 Section 4 - RedCap UE capability constraints; relevant to RedCap capability signaling and 1Rx/HD-FDD project assumptions.
- TS 38.101-1 Section 5.3 - FR1 bandwidth constraints; project uses 106 PRB cell with RedCap BWP size 51 for 30 kHz SCS. Exact RedCap clause mapping: Needs Verification.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| 30 UE burst smoke, 2s start gap | FAIL | UE1..UE30 runtime | 6/30 attach+PDU+TUN+ping; gNB restart 0; failures mostly RAR/RA window/Msg4 |
| 30 UE staged smoke, 8s start gap | FAIL | UE1..UE30 runtime | 26/30 attach+PDU+TUN+ping; UE11/20/26/29 missing TUN; gNB restart 0 |
| CN subscriber overlay | PASS | IMSI 001010000000001..050 generated | MySQL running; failures are not missing-subscriber failures |
| RedCap RAR LDPC regression check | PASS | UE failed logs | No LDPC decode failed / all-zero PDU marker found in failed UE logs |
| Full spec compliance | FAIL / Needs Verification | Runtime + local spec notes | Runtime does not prove full 3GPP conformance; 30/30 access not achieved |

## Known Issues / Blockers
- 30 UE all-access is not passing yet: best staged result is 26/30.
- gNB logs show heavy RA pressure: `Cannot find free vrb_map`, `exceeded RA window`, and `RA Procedure failed at Msg4`.
- Failed UEs can decode SIB1 and often receive RAR/Msg3, but do not reach stable Registration Accept / PDU Session / TUN.
- The mMTC path logs Msg2 DCI with `coreset_id=0` and BWP size 48 in many attempts; this differs from the earlier Case B fixed-UE path using nonzero CORESET/BWP51 and needs spec/design review.

## Next Step
- Investigate gNB RA/Msg4 scheduler behavior under RedCap mMTC load: `Cannot find free vrb_map`, RA window expiry, contention resolution timer expiry, and whether the mMTC path should use the RedCap nonzero CORESET/BWP51 Msg2 path consistently.
