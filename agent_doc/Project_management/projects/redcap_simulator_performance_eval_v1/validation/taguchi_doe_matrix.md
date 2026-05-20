# P2 Taguchi DOE Matrix

## Scope
- Milestone: P2
- Task IDs: P2-T1, P2-T2
- Source metric baseline: `literature/p1_metric_baseline.md`
- Runtime helper checked:
  - `ci-scripts/redcap_runtime_menu.sh`
  - `ci-scripts/redcap_mmtc_smoke_validation.sh`
- CSV run matrix:
  - `analysis/data/p2_taguchi_l9_run_matrix.csv`
- Success criteria:
  - `validation/success_criteria.md`

## Engineering Decision
- Use [L9 orthogonal array] for the first executable RFsim DOE.
- Use 3 active factors and 1 dummy column:
  - [A] UE scale
  - [B] UDP uplink offered rate
  - [C] validation sample depth
  - [D] dummy / error column
- Keep [single UE] as a calibration baseline outside the L9 matrix.
- Exclude [DL throughput] from first DOE because current helper is UL-only.
- Exclude [SNR/BLER/MIL/MCL] because RFsim does not expose these as direct controlled axes.

## Baseline Run Outside L9
| Baseline ID | Purpose | Command Factors | Responses |
|---|---|---|---|
| DOE-BASE-001 | Confirm single sampled UE user-plane and latency baseline before scaled DOE | `MMTC_TOTAL_UES=29`, `MMTC_SAMPLE_UES=1`, `MMTC_IPERF_RATE=85M`, UDP UL, duration 30s | throughput, jitter, loss, ping RTT, attach/PDU/tunnel, gNB restart |

## Factor And Level Matrix
| Factor | Level 1 | Level 2 | Level 3 | Runtime Knob | Paper / Project Basis |
|---|---|---|---|---|---|
| [A] UE scale / runtime compose pool | 29 UEs | 32 UEs | 56 UEs | `MMTC_TOTAL_UES` | PAPER-02 scheduled UE pressure; P1 project runtime history; helper requires total UEs > 28 |
| [B] UDP uplink offered rate | 10M | 50M | 85M | `MMTC_IPERF_RATE` | PAPER-06/PAPER-07 throughput baseline; current helper default 85M |
| [C] validation sample depth | 1 UE | 4 UEs | 8 UEs | `MMTC_SAMPLE_UES`, `MMTC_IPERF_SAMPLE_UES=all` | PAPER-02 UE load pressure; runtime cost control |
| [D] dummy column | D1 | D2 | D3 | no runtime effect | reserve column for residual/error visibility |

## Fixed Conditions
| Setting | Value | Reason |
|---|---|---|
| gNB config | default `GNB_REDCAP_CONFIG` from runtime menu | Current Case B accepted runtime path |
| CN compose | default `MMTC_CN_COMPOSE` | Keep CN path stable |
| iperf mode | UDP uplink | Current helper explicitly supports UL iperf |
| iperf duration | 30s | Matches training baseline |
| forward ping mode | parallel | Matches current menu defaults |
| reverse ping | disabled | Reduces runtime cost and focuses on forward user-plane path |
| PUCCH fallback | enabled | Current smoke helper exports `MMTC_PUCCH_COMMON_FALLBACK_BWP0=1` |
| DL iperf | not included | Existing helper does not expose DL iperf |

## L9 Orthogonal Array
| Run ID | A: UE scale | B: UL rate | C: sample depth | D: dummy | Total UEs | Sample UEs | iperf sample UEs | Rate |
|---|---:|---:|---:|---|---:|---|---|---|
| DOE-L9-01 | 1 | 1 | 1 | D1 | 29 | `1` | `all` | 10M |
| DOE-L9-02 | 1 | 2 | 2 | D2 | 29 | `1 6 11 16` | `all` | 50M |
| DOE-L9-03 | 1 | 3 | 3 | D3 | 29 | `1 3 5 7 9 11 13 16` | `all` | 85M |
| DOE-L9-04 | 2 | 1 | 2 | D3 | 32 | `1 11 22 32` | `all` | 10M |
| DOE-L9-05 | 2 | 2 | 3 | D1 | 32 | `1 5 9 13 17 21 25 32` | `all` | 50M |
| DOE-L9-06 | 2 | 3 | 1 | D2 | 32 | `1` | `all` | 85M |
| DOE-L9-07 | 3 | 1 | 3 | D2 | 56 | `1 8 16 24 32 40 48 56` | `all` | 10M |
| DOE-L9-08 | 3 | 2 | 1 | D3 | 56 | `1` | `all` | 50M |
| DOE-L9-09 | 3 | 3 | 2 | D1 | 56 | `1 19 38 56` | `all` | 85M |

## Execution Template
```bash
MMTC_TOTAL_UES=<total_ues> \
MMTC_SAMPLE_UES="<sample_ues>" \
MMTC_IPERF_SAMPLE_UES=all \
MMTC_IPERF_ENABLE=1 \
MMTC_IPERF_UDP=1 \
MMTC_IPERF_RATE=<rate> \
MMTC_IPERF_DURATION=30 \
MMTC_FORWARD_PING_MODE=parallel \
MMTC_RUN_REVERSE_PING=0 \
bash ci-scripts/redcap_mmtc_smoke_validation.sh
```

## Response Metrics
| Response | Unit | Source | S/N Direction | Paper Basis |
|---|---:|---|---|---|
| Receiver throughput | Mbit/s | iperf receiver line | Larger is better | PAPER-06/PAPER-07 |
| Sender throughput | Mbit/s | iperf sender line | Larger is better | PAPER-06/PAPER-07 |
| UDP jitter | ms | iperf receiver line | Smaller is better | simulator stability metric |
| UDP loss | percent | iperf receiver line | Smaller is better | PAPER-02 reliability proxy |
| Forward ping success | ratio | smoke summary | Larger is better | user-plane readiness |
| Attach/PDU/tunnel success | ratio | smoke summary | Larger is better | PAPER-07 access traceability |
| gNB restart count | count | smoke summary / Docker inspect | Smaller is better | platform stability |
| Failure count | count | smoke summary | Smaller is better | platform stability |

## Validation Mapping
| Validation ID | Covered By | Notes |
|---|---|---|
| PERF-BASE-001 | DOE-BASE-001 | single UE UDP UL throughput baseline |
| PERF-LAT-001 | DOE-BASE-001 and L9 sample pings | ping RTT proxy; not full 5G E2E latency |
| PERF-SCALE-001 | DOE-L9-01..09 | UE scale levels 16/32/56 |
| PERF-LOAD-001 | DOE-L9-01..09 | offered rates 10M/50M/85M |
| PERF-STAB-001 | all runs | gNB restart and failure markers |

## Known Limitations
- [PDCCH blocking probability] is not directly measured; use RA/control pressure markers only.
- [DL throughput] remains out of first DOE until helper support is added.
- [SNR/BLER/MIL/MCL] from PAPER-03/PAPER-04 are link-level or link-budget metrics and are not direct RFsim axes.
- [Interaction effects] are limited because the first L9 design uses only main-effect screening.
- [Sample depth] is a validation-cost factor, not true simultaneous traffic concurrency. Current smoke script runs selected iperf checks sequentially.
- [Runtime minimum compose pool] is 29 because `generate_mmtc_overlay.sh` extends a fixed UE1..UE28 base compose and rejects `MMTC_TOTAL_UES <= 28`.

## P2 Decision
- First executable DOE: [DOE-BASE-001] plus [DOE-L9-01..09].
- Primary response for platform-validity trend: [Receiver throughput Mbps].
- Secondary responses: [UDP loss], [jitter], [forward ping success], [attach/PDU/tunnel success], [gNB restart count].
- P3 pass/fail classification must use `validation/success_criteria.md`.
