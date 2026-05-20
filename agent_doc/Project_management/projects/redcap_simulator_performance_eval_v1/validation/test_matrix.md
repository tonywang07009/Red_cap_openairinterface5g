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
| PERF-BASE-001 | single-UE UDP uplink throughput baseline | UE=1, UDP iperf | throughput, jitter, packet loss | [ ] |
| PERF-LAT-001 | single-UE latency baseline | UE=1, ping/RTT proxy | min/avg/max RTT, loss | [ ] |
| PERF-SCALE-001 | staged UE count scaling | DOE UE-count levels | attach/PDU/tunnel success ratio | [ ] |
| PERF-LOAD-001 | offered-rate sweep | DOE traffic-rate levels | sender/receiver Mbps and loss | [ ] |
| PERF-STAB-001 | runtime stability check | each DOE run | gNB restart count, failure markers | [ ] |

## Evidence Requirements
- Raw log path.
- Parsed CSV row.
- Plot path when applicable.
- Relevant paper metric mapping when claiming comparison.
