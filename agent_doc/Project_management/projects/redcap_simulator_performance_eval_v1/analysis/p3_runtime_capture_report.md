# P3 Runtime Capture Report

## Summary
- Milestone: P3 Runtime Metric Capture
- Dataset: `analysis/data/p3_runtime_metrics.csv`
- Raw logs: `analysis/data/p3_raw/` and `test_log/compiler_logs/mmtc_smoke_*`
- Status: [COMPLETED]
- Dataset decision: [Strong Dataset]

## Success Criteria Check
| Criterion | Result |
|---|---|
| `DOE-BASE-001` passes | PASS |
| At least 7 of 9 L9 rows are [PASS] or [PASS_WITH_GAP] | PASS, 9/9 |
| No unclassified [FAIL] remains | PASS |
| Every [FAIL]/[BLOCKED]/[PASS_WITH_GAP] has failure-to-improvement record | PASS |
| All 10 rows are [PASS] or [PASS_WITH_GAP] | PASS |
| At least 8 rows have receiver throughput parsed | PASS, 10/10 |
| `gnb_restart_count = 0` for all rows | PASS |
| Trends can be plotted without dropping failed rows | PASS |

## Runtime Result Table
| Run ID | Status | Total UEs | Sample Count | Rate | Receiver Mbps | Sender Mbps | Jitter ms | UDP Loss % | RTT Avg ms | gNB Restart |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DOE-BASE-001 | [PASS] | 29 | 1 | 85M | 84.900 | 85.000 | 0.216 | 0.000 | 4.165 | 0 |
| DOE-L9-01 | [PASS] | 29 | 1 | 10M | 9.990 | 10.000 | 1.511 | 0.000 | 3.983 | 0 |
| DOE-L9-02 | [PASS] | 29 | 4 | 50M | 49.900 | 50.000 | 0.397 | 0.000 | 12.673 | 0 |
| DOE-L9-03 | [PASS] | 29 | 8 | 85M | 30.063 | 85.000 | 0.305 | 0.000 | 30.448 | 0 |
| DOE-L9-04 | [PASS] | 32 | 4 | 10M | 9.980 | 10.000 | 1.861 | 0.000 | 12.893 | 0 |
| DOE-L9-05 | [PASS] | 32 | 8 | 50M | 30.275 | 50.000 | 0.431 | 0.000 | 31.500 | 0 |
| DOE-L9-06 | [PASS] | 32 | 1 | 85M | 84.900 | 85.000 | 0.228 | 0.000 | 3.663 | 0 |
| DOE-L9-07 | [PASS] | 56 | 8 | 10M | 9.979 | 10.000 | 1.630 | 0.000 | 30.457 | 0 |
| DOE-L9-08 | [PASS] | 56 | 1 | 50M | 49.900 | 50.000 | 0.241 | 0.000 | 3.928 | 0 |
| DOE-L9-09 | [PASS] | 56 | 4 | 85M | 69.075 | 85.000 | 0.129 | 0.000 | 14.134 | 0 |

## Engineering Observations
- All completed rows passed hard runtime criteria.
- Attach, PDU session, tunnel readiness, and forward ping were 100% in all rows.
- UDP loss was 0% in all rows.
- gNB restart count was 0 in all rows.
- Throughput gap appears in:
  - `DOE-L9-03`: sender 85.000 Mbps, receiver 30.063 Mbps.
  - `DOE-L9-05`: sender 50.000 Mbps, receiver 30.275 Mbps.
  - `DOE-L9-09`: sender 85.000 Mbps, receiver 69.075 Mbps.

## P4 Plotting Inputs
- Primary CSV: `analysis/data/p3_runtime_metrics.csv`
- Recommended P4 plots:
  - receiver Mbps vs run ID
  - sender vs receiver Mbps by run ID
  - RTT avg vs sample count
  - jitter vs sample count
  - UDP loss vs run ID
  - gNB restart count vs run ID

## Interpretation Guardrail
- This dataset supports RFsim runtime trend analysis.
- Do not claim absolute paper-level throughput equivalence until RFsim radio/config equivalence is documented.
- Treat sender/receiver throughput gaps as a key P4/P5 analysis target.
