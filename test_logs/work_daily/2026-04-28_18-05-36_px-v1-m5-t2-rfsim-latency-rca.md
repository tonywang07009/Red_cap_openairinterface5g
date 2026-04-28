# Work Daily Log
## Session Metadata
- Date: 2026-04-28 18:05
- Agent Session ID: N/A
- Task Slug: px-v1-m5-t2-rfsim-latency-rca
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md
- Task ID: M5-T2
- Batch: B

## Milestone & Sub-task Reference
- Milestone: M5 - Compose + mMTC staged validation
- Sub-task: 50 active UE scheduler/RFsim latency bottleneck RCA
- Status: COMPLETED

## What Was Done
- Built/updated symdex index for this repository before code and log lookup.
- Added `ci-scripts/redcap_mmtc_latency_rca.py`.
- Parsed existing 2026-04-28 stage50 logs into RCA Markdown reports.
- Generated:
  - `test_log/compiler_logs/mmtc_latency_rca_2026-04-28_12-05-26.md`
  - `test_log/compiler_logs/mmtc_latency_rca_2026-04-28_12-21-23.md`
  - `test_log/compiler_logs/mmtc_latency_rca_2026-04-28_12-40-05.md`
- Confirmed active 50 UE runs had TCP receiver throughput around 1.07..2.05 Mbps.
- Confirmed stop-quiesce run restored UE1 TCP throughput to 20.0 Mbps.
- Confirmed active 50 UE runs show high ping RTT and UE simulated-time drift around 9.6x wall/sim ratio.
- Cross-checked RFsim code paths:
  - `radio/rfsimulator/simulator.cpp:rfsimulator_write_internal()`
  - `radio/rfsimulator/simulator.cpp:rfsimulator_read_internal()`
  - `radio/rfsimulator/simulator.cpp:combine_received_beams()`

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.4 - UL scheduling and HARQ behavior relevance for delayed TCP UL delivery. Exact log-to-clause mapping: ⚠ Needs Verification.
- TS 38.321 Section 5.7 - Connected DRX is the next low-power MAC behavior target.
- TS 38.306 Section 4 - RedCap UE capability framework. Exact eRedCap 20 Mbps capability mapping: ⚠ Needs Verification.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| symdex repository index | PASS | code lookup | repo indexed before investigation |
| Python syntax check | PASS | `ci-scripts/redcap_mmtc_latency_rca.py` | `python3 -m py_compile` passed |
| RCA report 12-05 active50 | PASS | RTT, TCP, sim-time drift | avg RTT 687.965 ms; TCP receiver 1.07..2.05 Mbps |
| RCA report 12-21 active50 | PASS | RTT, TCP, sim-time drift | avg RTT 763.359 ms; UE1 receiver 1.20 Mbps |
| RCA report 12-40 stop-quiesce | PASS | RTT, TCP, sim-time drift | UE1 sender/receiver 20.0 Mbps |

## Known Issues / Blockers
- 50 active RFsim UE processes still advance simulated time much slower than wall time.
- `docker pause` does not recover TCP because paused UE RFsim sockets remain connected and can still disturb the RFsim timing path.
- `docker stop` recovers selected UE throughput because non-selected UE RFsim connections are removed.
- Full R18 eRedCap capability signaling is still not implemented in the current branch.

## Next Step
- Start M4B-T1: inspect and implement minimum Connected DRX path, beginning with `openair2/LAYER2/NR_MAC_UE/config_ue.c` handling of `drx-Config`.
