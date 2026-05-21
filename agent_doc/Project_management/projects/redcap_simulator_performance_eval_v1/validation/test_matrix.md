# RedCap Simulator Performance Validation Matrix

## Validation Legend
- [PASS]: required metric captured and meets the current criterion.
- [FAIL]: metric captured but violates the criterion.
- [BLOCKED]: run could not complete due to environment/tooling issue.
- [NA]: not applicable to the current run.

## Runtime Tests
| Test ID | Purpose | Input | Required Output | Status |
|---|---|---|---|---|
| PERF-DOE-001 | Taguchi L9 DOE design | P1 metric baseline | factor/level table and run matrix | [x] |
| PERF-CRIT-001 | Success criteria and failure-to-improvement model | P1/P2 outputs | hard pass, trend criteria, failure categories | [x] |
| PERF-BASE-001 | single sampled UE UDP uplink throughput baseline | `MMTC_TOTAL_UES=29`, `MMTC_SAMPLE_UES=1`, UDP iperf | throughput, jitter, packet loss | [x] |
| PERF-LAT-001 | single-UE latency baseline | UE=1, ping/RTT proxy | min/avg/max RTT, loss | [x] |
| PERF-SCALE-001 | staged UE count scaling | DOE UE-count levels | attach/PDU/tunnel success ratio | [x] |
| PERF-LOAD-001 | offered-rate sweep | DOE traffic-rate levels | sender/receiver Mbps and loss | [x] |
| PERF-STAB-001 | runtime stability check | each DOE run | gNB restart count, failure markers | [x] |

## Partial P3 Evidence
- `DOE-BASE-001` and `DOE-L9-01..09` are complete.
- All completed rows are [PASS].
- `DOE-L9-03`, `DOE-L9-05`, and `DOE-L9-09` show sender/receiver throughput gaps while still meeting hard pass criteria.

## Evidence Requirements
- Raw log path.
- Parsed CSV row.
- Plot path when applicable.
- Relevant paper metric mapping when claiming comparison.
- Status classification from `validation/success_criteria.md`.
- Failure-to-improvement record for every [FAIL], [BLOCKED], [PASS_WITH_GAP], or [INVALID] run.
