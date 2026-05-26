# P3 Runtime Metric Capture

## 2026-05-25 Evidence Cleanup Note
- Current retained Paper 07 raw evidence was promoted to `redcap_library/library_runtime_probe/`.
- New runtime captures should still write timestamped raw logs under `test_log/compiler_logs/` before promotion.

## Milestone Metadata
- Milestone: P3
- Task IDs: P3-T1, P3-T2, P3-T3
- Status: [COMPLETED]
- P3-T1 Status: [COMPLETED]
- P3-T2 Status: [COMPLETED]
- P3-T3 Status: [COMPLETED]

## Purpose
- Convert the DOE run matrix into repeatable RFsim runs and CSV metrics.

## Runtime Sources
- Scenario directory: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`
- Current helper: `redcap_interface/redcap_runtime_menu.sh`
- Logs: `test_log/compiler_logs/`, `test_log/runtime_artifacts/`
- Run matrix: `analysis/data/p2_taguchi_l9_run_matrix.csv`
- Success criteria: `validation/success_criteria.md`
- P3 runner/parser: `analysis/scripts/p3_capture_workflow.py`
- P3 metrics CSV: `analysis/data/p3_runtime_metrics.csv`
- P3 failure-to-improvement CSV: `analysis/data/p3_failure_to_improvement_log.csv`

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
- [ ] Every [FAIL], [BLOCKED], [PASS_WITH_GAP], or [INVALID] run has a failure-to-improvement record.
- [ ] Final P3 report states whether the collected dataset is [Minimum Acceptable Dataset], [Strong Dataset], or [Insufficient Dataset].

## P3-T1 Runtime Capture Workflow

### Step 1: List DOE Rows
```bash
python3 agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/scripts/p3_capture_workflow.py list-runs
```

### Step 2: Review One Run Command Before Execution
```bash
python3 agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/scripts/p3_capture_workflow.py command --run-id DOE-BASE-001
```

### Step 3: Execute One DOE Row
```bash
python3 agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/scripts/p3_capture_workflow.py run --run-id DOE-BASE-001
```

### Step 4: Parse An Existing Smoke Log Prefix
```bash
python3 agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/scripts/p3_capture_workflow.py parse-existing \
  --run-id DOE-BASE-001 \
  --log-prefix 2026-05-20_18-02-35
```

## Classification Rule
- [PASS]: hard pass criteria satisfied and required metrics parsed.
- [PASS_WITH_GAP]: runtime looks valid, but smoke summary or receiver-side measurement is missing.
- [FAIL]: hard pass criteria failed after runtime completed.
- [BLOCKED]: smoke run or environment prevented measurement.
- [INVALID]: run metadata/log prefix cannot support interpretation.

## Current P3 Entry Decision
- Start with `DOE-BASE-001` before running all L9 rows.
- Do not treat old smoke logs as formal P3 evidence unless explicitly parsed and labelled.
- Use old smoke logs only to validate parser behavior before formal DOE execution.

## P3-T1 Validation Performed
- `list-runs` confirmed `DOE-BASE-001` plus `DOE-L9-01..09` are readable from the P2 CSV.
- `command --run-id DOE-BASE-001` produced the expected smoke-validation environment variables.
- `parse-existing --run-id DOE-BASE-001 --log-prefix 2026-05-20_18-02-35 --no-write` parsed:
  - receiver throughput: 84.9 Mbit/s
  - sender throughput: 85.0 Mbit/s
  - UDP jitter: 0.182 ms
  - UDP loss: 0%
  - RTT avg: 3.918 ms
  - classification: [PASS_WITH_GAP], because old logs do not include wrapper stdout summary.
- `python3 -m py_compile` passed for `analysis/scripts/p3_capture_workflow.py`.

## P3-T2 Preflight Finding
- First formal `DOE-BASE-001` attempt was [BLOCKED].
- Evidence:
  - `analysis/data/p3_raw/DOE-BASE-001/2026-05-20_22-30-06/smoke_stdout.log`
  - message: `TOTAL_UES must be greater than 28 to extend the fixed-UE base compose`
- Interpretation:
  - The original P2 baseline used `MMTC_TOTAL_UES=1`, but the current runtime helper requires `MMTC_TOTAL_UES > 28`.
  - This is a [workflow / experiment-design correction], not a RF throughput failure.
- Correction:
  - `DOE-BASE-001` now uses `MMTC_TOTAL_UES=29`, `MMTC_SAMPLE_UES=1`.
  - L9 rows with previous `total_ues=16` now use `total_ues=29` as the minimum executable compose pool.

## P3-T2 Baseline Result
- Formal run: `DOE-BASE-001`
- Log prefix: `2026-05-20_22-32-25`
- Status: [PASS]
- Result row:
  - receiver throughput: 84.9 Mbit/s
  - sender throughput: 85.0 Mbit/s
  - UDP jitter: 0.216 ms
  - UDP loss: 0%
  - ping RTT min/avg/max: 2.908 / 4.165 / 5.548 ms
  - attach/PDU/tunnel/forward ping: 100%
  - gNB restart count: 0
  - failure count: 0
- Evidence:
  - `analysis/data/p3_runtime_metrics.csv`
  - `analysis/data/p3_raw/DOE-BASE-001/2026-05-20_22-32-25/smoke_stdout.log`
  - `test_log/compiler_logs/mmtc_smoke_2026-05-20_22-32-25_ue1_iperf3_ul.log`
  - `test_log/compiler_logs/mmtc_smoke_2026-05-20_22-32-25_ue1_ping.log`

## P3-T3 Next Execution
- P3-T3 is complete.
- After each row:
  - inspect status in `analysis/data/p3_runtime_metrics.csv`,
  - keep failure rows instead of deleting them,
  - use `analysis/data/p3_failure_to_improvement_log.csv` for required improvement records.

## P3-T3 Partial L9 Results
| Run ID | Status | Total UEs | Sample UEs | Rate | Receiver Mbps | Sender Mbps | Jitter ms | UDP Loss % | RTT Avg ms | gNB Restart | Notes |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| DOE-L9-01 | [PASS] | 29 | `1` | 10M | 9.990 | 10.000 | 1.511 | 0.000 | 3.983 | 0 | low-rate single sampled UE |
| DOE-L9-02 | [PASS] | 29 | `1 6 11 16` | 50M | 49.900 | 50.000 | 0.397 | 0.000 | 12.673 | 0 | 4 sampled UEs |
| DOE-L9-03 | [PASS] | 29 | `1 3 5 7 9 11 13 16` | 85M | 30.063 | 85.000 | 0.305 | 0.000 | 30.448 | 0 | throughput gap observed |
| DOE-L9-04 | [PASS] | 32 | `1 11 22 32` | 10M | 9.980 | 10.000 | 1.861 | 0.000 | 12.893 | 0 | 4 sampled UEs |
| DOE-L9-05 | [PASS] | 32 | `1 5 9 13 17 21 25 32` | 50M | 30.275 | 50.000 | 0.431 | 0.000 | 31.500 | 0 | throughput gap observed |
| DOE-L9-06 | [PASS] | 32 | `1` | 85M | 84.900 | 85.000 | 0.228 | 0.000 | 3.663 | 0 | high-rate single sampled UE |
| DOE-L9-07 | [PASS] | 56 | `1 8 16 24 32 40 48 56` | 10M | 9.979 | 10.000 | 1.630 | 0.000 | 30.457 | 0 | 8 sampled UEs |
| DOE-L9-08 | [PASS] | 56 | `1` | 50M | 49.900 | 50.000 | 0.241 | 0.000 | 3.928 | 0 | mid-rate single sampled UE |
| DOE-L9-09 | [PASS] | 56 | `1 19 38 56` | 85M | 69.075 | 85.000 | 0.129 | 0.000 | 14.134 | 0 | throughput gap observed |

## Final P3 Dataset Decision
- Dataset class: [Strong Dataset]
- Basis:
  - `DOE-BASE-001` passed.
  - `DOE-L9-01..09` all passed.
  - All 10 rows have receiver-side throughput parsed.
  - All 10 rows have `gnb_restart_count = 0`.
  - No failed rows need to be dropped before P4 plotting.
- Limitation for P4/P5:
  - `DOE-L9-03`, `DOE-L9-05`, and `DOE-L9-09` show sender/receiver throughput gaps.
  - These are not hard failures, but they must be interpreted as RFsim runtime behavior before claiming paper-level performance equivalence.
