# Work Daily Log
## Session Metadata
- Date: 2026-04-28 12:48
- Agent Session ID: N/A
- Task Slug: px-v1-m5-t2-eredcap20-tcp-stop-quiesce
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: M5 - Compose + mMTC staged validation
- Sub-task: M5-T2 scalable mMTC staged validation with eRedCap20 TCP profile
- Status: COMPLETED

## What Was Done
- Added TCP iperf3 receiver-throughput parsing and minimum Mbps enforcement in ci-scripts/redcap_mmtc_smoke_validation.sh.
- Added MMTC_IPERF_PROFILE=eredcap20_tcp defaults in ci-scripts/redcap_mmtc_stage_scan.sh: 20M TCP, 20s duration, 20 Mbps receiver threshold.
- Added MMTC_IPERF_QUIESCE_NON_SELECTED and MMTC_IPERF_QUIESCE_ACTION controls.
- Verified that action=pause does not recover TCP after 50 active RFsim UE load; UE1 iperf3 connection timed out.
- Added action=stop mode to stop non-selected UE containers after 50 UE attach/ping, then validate selected UE TCP throughput.
- Confirmed 50/50 UE attach, PDU, TUN, forward ping, and selected UE1 TCP receiver throughput of 20.000000 Mbit/s.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4 - UE radio access capability framework; RedCap/eRedCap capability interpretation remains partially implementation-dependent in this branch. ⚠ Needs Verification for exact eRedCap 20 Mbps mapping.
- TS 38.101-1 Section 5.3 - FR1 channel bandwidth constraints; project baseline caps RedCap/eRedCap RFsim profile at 20 MHz.
- TS 38.321 Section 5.4 - UL scheduling/HARQ behavior; relevant to observed SR/UL scheduling pressure under 50 active RFsim UEs. ⚠ Needs Verification for exact scheduler log-to-clause mapping.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| bash syntax check | PASS | ci-scripts/redcap_mmtc_stage_scan.sh, ci-scripts/redcap_mmtc_smoke_validation.sh | bash -n completed with rc=0 |
| 1 UE eRedCap20 TCP profile | PASS | UE1 attach, PDU, TUN, ping, TCP UL iperf3 | receiver=20.000000 Mbit/s |
| 50 UE active TCP without quiesce | FAIL | 50 UE attach/ping OK, UE1/25/50 TCP sampled | receiver about 1-2 Mbit/s under 50 active RFsim load |
| 50 UE active TCP with pause quiesce | FAIL | 50 UE attach/ping OK, UE1 TCP sampled | iperf3 connection timed out after pausing 49 UEs |
| 50 UE TCP with stop quiesce | PASS | 50/50 attach, PDU, TUN, forward ping; UE1 TCP UL | command used MMTC_IPERF_QUIESCE_ACTION=stop; receiver=20.000000 Mbit/s |

## Known Issues / Blockers
- 50 concurrently active RFsim UE processes still create high ping latency and cannot sustain 20 Mbps TCP per selected UE without stopping non-selected UEs.
- Current branch has RedCap support fields, but full Release 18 eRedCap capability signaling support was not found in the existing C/YAML path. Treat eredcap20_tcp as a validation profile, not full R18 eRedCap capability conformance.
- To make 50 active UEs simultaneously sustain higher TCP throughput, next work must inspect gNB MAC scheduler/RFsim capacity and SR/UL grant pressure.

## Next Step
- Continue M5/M4B follow-up: investigate 50-active-UE scheduler/RFsim latency bottleneck, then proceed with Simluation_v2 DRX/eDRX/PSM low-power mMTC behavior.
