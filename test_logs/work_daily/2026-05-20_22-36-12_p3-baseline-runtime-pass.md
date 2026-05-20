# Work Daily Log
## Session Metadata
- Date: 2026-05-20 22:36
- Agent Session ID: N/A
- Task Slug: p3-baseline-runtime-pass
- Project Path: agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: P3 Runtime Metric Capture
- Sub-task: P3-T2 Run baseline throughput and latency validation
- Status: [COMPLETED]

## What Was Done
- Ran formal `DOE-BASE-001` RFsim baseline through `analysis/scripts/p3_capture_workflow.py`.
- Corrected P2/P3 runtime matrix so `DOE-BASE-001` uses `MMTC_TOTAL_UES=29`, `MMTC_SAMPLE_UES=1`.
- Corrected L9 rows with previous `total_ues=16` to use runtime-minimum `total_ues=29`.
- Wrote formal baseline result to `analysis/data/p3_runtime_metrics.csv`.
- Added failure-to-improvement records for two preflight blockers:
  - original `MMTC_TOTAL_UES=1` rejected by runtime helper,
  - Docker API permission denied before escalated execution.
- Updated `project_plan.md`: P3-T2 is completed and P3-T3 was added for DOE-L9 capture.
- Updated `milestones/P3_runtime_metric_capture.md` with baseline evidence and next L9 execution step.
- Updated `validation/test_matrix.md` so `PERF-BASE-001` is complete.

## 3GPP Spec Clauses Referenced
- N/A — this task ran RFsim runtime validation and did not modify PHY/MAC/RRC behavior.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| DOE-BASE-001 formal runtime | PASS | single sampled UE, UDP UL, ping RTT | status `[PASS]` |
| Receiver throughput | PASS | iperf3 receiver | 84.9 Mbit/s |
| Sender throughput | PASS | iperf3 sender | 85.0 Mbit/s |
| UDP jitter | PASS | iperf3 receiver | 0.216 ms |
| UDP loss | PASS | iperf3 receiver | 0% |
| Ping RTT | PASS | UE to ext-dn tunnel target | min/avg/max = 2.908 / 4.165 / 5.548 ms |
| Attach/PDU/tunnel/forward ping | PASS | smoke summary | 100% |
| gNB restart count | PASS | smoke summary / docker inspect | 0 |
| Failure-to-improvement logging | PASS | two preflight blockers | records added to `p3_failure_to_improvement_log.csv` |
| Python workflow syntax | PASS | `p3_capture_workflow.py` | `python3 -m py_compile` passed |
| Source build | N/A | No C/C++ source changed | Build not required |

## Known Issues / Blockers
- P3 is not complete until DOE-L9 rows are executed or explicitly deferred.
- Current helper measures sampled UE traffic; paper-level UE-scale claims must be phrased as RFsim/runtime trend claims unless stronger simultaneous-load instrumentation is added.

## Next Step
- Run `DOE-L9-01` through `analysis/scripts/p3_capture_workflow.py run --run-id DOE-L9-01`, inspect CSV status, then continue L9 sequentially if the row is stable.
