# P3 Runtime Metric Capture

## Milestone Metadata
- Milestone: P3
- Task IDs: P3-T1, P3-T2
- Status: [NOT STARTED]

## Purpose
- Convert the DOE run matrix into repeatable RFsim runs and CSV metrics.

## Runtime Sources
- Scenario directory: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`
- Current helper: `ci-scripts/redcap_runtime_menu.sh`
- Logs: `test_log/compiler_logs/`, `test_log/runtime_artifacts/`

## Required Metrics
- throughput: iperf sender/receiver Mbps
- latency: ping RTT or selected RTT proxy
- jitter: iperf UDP jitter
- packet loss: ping loss and iperf UDP datagram loss
- runtime stability: gNB restart count, UE attach/PDU/tunnel status

## Acceptance Criteria
- [ ] Every run writes raw log output.
- [ ] Every run produces one CSV row.
- [ ] Failure rows are preserved and not silently dropped.
- [ ] RFsim status is reported as [PASS], [FAIL], or [BLOCKED].
