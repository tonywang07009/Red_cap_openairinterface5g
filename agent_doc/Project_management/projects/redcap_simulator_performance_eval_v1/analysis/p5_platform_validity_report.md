# P5 Platform Validity Report

## Executive Decision
- Final decision: [VALID FOR TREND STUDY]
- Valid scope:
  - RedCap RFsim UDP uplink throughput trend study.
  - RTT proxy latency trend study.
  - UDP jitter and packet-loss runtime stability study.
  - Attach, PDU session, tunnel readiness, forward ping, and gNB restart stability checks.
- Invalid or not-yet-valid scope:
  - Absolute paper-equivalent throughput claims.
  - Field-trial or link-level channel claims.
  - SNR, BLER, MIL, MCL, coverage recovery, and SUL performance claims.
  - True PDCCH blocking probability.
  - DL throughput comparison.

## Evidence Base
| Evidence Type | Source | Status |
|---|---|---|
| [Measured] | `analysis/data/p3_runtime_metrics.csv` | 10/10 rows [PASS] |
| [Measured] | `analysis/p3_runtime_capture_report.md` | [Strong Dataset] |
| [Measured] | `analysis/p4_matplotlib_plot_report.md` | P4 plots generated |
| [Paper Evidence] | `literature/p1_metric_baseline.md` | PAPER-06/PAPER-07 throughput and latency anchors |
| [Paper Evidence] | `literature/p1_metric_baseline.md` | PAPER-02 UE/control pressure rationale |
| [Paper Evidence] | `literature/p1_metric_baseline.md` | PAPER-03/PAPER-04 channel-model limitations |
| [3GPP Evidence] | Project traceability seeds in `project_plan.md` | TS 38.306 / TS 38.321 / TS 38.331 / TS 38.214 [Needs Verification] |

## Technical Background
- [Measured] The current platform uses OAI RFsim and the RedCap RFsim compose path under `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`.
- [Measured] P3 used UDP uplink `iperf3` and `ping` as the performance measurement tools.
- [Measured] The P2/P3 DOE controls simulator-observed factors:
  - total UE compose pool,
  - sampled UE count,
  - UDP uplink offered rate.
- [Inference] These factors are sufficient for first-pass RFsim load and offered-rate trend analysis.
- [Inference] These factors are not sufficient for physical-layer channel equivalence.

## Literature Baseline
| Paper ID | P5 Use | Validity Impact |
|---|---|---|
| PAPER-06 | [Paper Evidence] RedCap throughput and latency performance | supports throughput/latency comparison target selection |
| PAPER-07 | [Paper Evidence] UDP peak-rate and RedCap access traceability | supports UDP UL baseline and access/runtime traceability |
| PAPER-02 | [Paper Evidence] scheduled UE / PDCCH pressure rationale | supports UE-scale pressure as a factor, but not true blocking claims |
| PAPER-01 | [Paper Evidence] ping latency and field-rate comparison | supports latency proxy context, not field equivalence |
| PAPER-03 | [Paper Evidence] coverage, BLER, SINR, MIL | marks RFsim channel-model gap |
| PAPER-04 | [Paper Evidence] UL/SUL link-level throughput and BLER | marks SNR/SUL/BLER gap |
| PAPER-05 | [Paper Evidence] wearable and low-power RedCap scenario | supports future low-power factors, not current P3 performance claims |

## Experiment Design
- [Measured] P2 defined one baseline run and nine L9 DOE runs.
- [Measured] Runtime matrix:
  - `DOE-BASE-001`
  - `DOE-L9-01..09`
- [Measured] Factors:
  - total UE compose pool: 29 / 32 / 56,
  - UDP offered rate: 10M / 50M / 85M,
  - sampled UE count: 1 / 4 / 8.
- [Measured] `MMTC_TOTAL_UES=29` is the minimum executable compose pool because the current helper extends a fixed UE1..UE28 base compose.
- [Inference] The first DOE is a screening design for trend discovery, not a complete interaction model.

## Runtime Results
| Run ID | Status | Total UEs | Sample Count | Rate | Receiver Mbps | Sender Mbps | RTT Avg ms | Jitter ms | UDP Loss % | gNB Restart |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DOE-BASE-001 | [PASS] | 29 | 1 | 85M | 84.900 | 85.000 | 4.165 | 0.216 | 0.000 | 0 |
| DOE-L9-01 | [PASS] | 29 | 1 | 10M | 9.990 | 10.000 | 3.983 | 1.511 | 0.000 | 0 |
| DOE-L9-02 | [PASS] | 29 | 4 | 50M | 49.900 | 50.000 | 12.673 | 0.397 | 0.000 | 0 |
| DOE-L9-03 | [PASS] | 29 | 8 | 85M | 30.063 | 85.000 | 30.448 | 0.305 | 0.000 | 0 |
| DOE-L9-04 | [PASS] | 32 | 4 | 10M | 9.980 | 10.000 | 12.893 | 1.861 | 0.000 | 0 |
| DOE-L9-05 | [PASS] | 32 | 8 | 50M | 30.275 | 50.000 | 31.500 | 0.431 | 0.000 | 0 |
| DOE-L9-06 | [PASS] | 32 | 1 | 85M | 84.900 | 85.000 | 3.663 | 0.228 | 0.000 | 0 |
| DOE-L9-07 | [PASS] | 56 | 8 | 10M | 9.979 | 10.000 | 30.457 | 1.630 | 0.000 | 0 |
| DOE-L9-08 | [PASS] | 56 | 1 | 50M | 49.900 | 50.000 | 3.928 | 0.241 | 0.000 | 0 |
| DOE-L9-09 | [PASS] | 56 | 4 | 85M | 69.075 | 85.000 | 14.134 | 0.129 | 0.000 | 0 |

## Plot Evidence
- [Measured] P4 generated these plot groups:
  - throughput vs offered rate,
  - throughput vs UE count,
  - RTT latency vs UE count,
  - jitter vs UE count,
  - packet loss vs UE count,
  - sender-receiver throughput gap by run.
- [Measured] Source:
  - `analysis/p4_matplotlib_plot_report.md`
  - `analysis/plots/`
- [Measured] All plot axes use simulator-controlled X variables and measured Y metrics.

## Claim Classification
| Claim | Classification | Decision |
|---|---|---|
| The platform can complete RedCap RFsim UDP UL baseline and L9 runtime runs without gNB restart. | [Measured] | Supported |
| The platform can produce receiver/sender throughput, jitter, packet loss, RTT, attach/PDU/tunnel, and gNB restart metrics. | [Measured] | Supported |
| The platform supports trend-level comparison for throughput and RTT proxy latency. | [Inference] from [Measured] + [Paper Evidence] | Supported with limits |
| PAPER-06/PAPER-07 throughput and latency are the closest paper anchors. | [Paper Evidence] | Supported |
| PAPER-02 justifies UE-count pressure as an experiment factor. | [Paper Evidence] | Supported as proxy only |
| RFsim reproduces paper absolute throughput values. | [Inference] | Not supported |
| RFsim reproduces PAPER-03/PAPER-04 SNR/BLER/MIL/MCL results. | [Paper Evidence] + [Measured] limitation | Not supported |
| RFsim measures true PDCCH blocking probability. | [Inference] | Not supported until instrumentation exists |
| RFsim validates DL RedCap throughput. | [Measured] limitation | Not supported in current P3/P4 |

## Paper Comparison
### Throughput
- [Paper Evidence] PAPER-06 and PAPER-07 include RedCap throughput and UDP peak-rate style evidence.
- [Measured] RFsim captured UDP UL sender and receiver throughput for all 10 rows.
- [Measured] Single sampled UE rows track offered rate closely:
  - 10M offered: 9.990 Mbps receiver.
  - 50M offered: 49.900 Mbps receiver.
  - 85M offered: 84.900 Mbps receiver.
- [Inference] The platform is credible for offered-rate trend study when sample count is low.
- [Measured] Throughput gaps appear under selected multi-sampled rows:
  - `DOE-L9-03`: gap 54.938 Mbps.
  - `DOE-L9-05`: gap 19.725 Mbps.
  - `DOE-L9-09`: gap 15.925 Mbps.
- [Inference] These gaps should be treated as RFsim runtime behavior requiring analysis, not as paper-equivalent RedCap degradation.

### Latency
- [Paper Evidence] PAPER-01 and PAPER-06 provide latency context.
- [Measured] RFsim captured ping RTT min/avg/max for all 10 rows.
- [Measured] RTT avg rises with sampled UE count:
  - single sampled UE rows are near 3.663 to 4.165 ms,
  - 4 sampled UE rows are near 12.673 to 14.134 ms,
  - 8 sampled UE rows are near 30.448 to 31.500 ms.
- [Inference] The platform is credible for RTT proxy trend study.
- [Limitation] This is not full 5G E2E latency equivalence.

### Reliability And Stability
- [Measured] UDP loss was 0% in all rows.
- [Measured] Ping loss was 0% in all rows.
- [Measured] gNB restart count was 0 in all rows.
- [Measured] Attach/PDU/tunnel/forward ping success ratios were 100% in all rows.
- [Inference] The platform is stable enough for this P3 DOE envelope.

### Control-Channel And Coverage
- [Paper Evidence] PAPER-02 targets PDCCH blocking probability.
- [Measured] P3 does not expose PDCCH candidate occupancy or blocking probability.
- [Inference] Current results can only support control-pressure proxy discussion through UE scaling and failure markers.
- [Paper Evidence] PAPER-03/PAPER-04 rely on channel/link-level metrics such as SNR, BLER, MIL, MCL, and SUL.
- [Measured] P3/P4 do not control or measure those axes.
- [Inference] Current platform is not valid for coverage/link-level paper reproduction.

## 3GPP Traceability
- [3GPP Evidence] TS 38.306 Section 4 is relevant to RedCap UE capability constraints. [Needs Verification]
- [3GPP Evidence] TS 38.321 Section 5.4 is relevant to UL-SCH data transfer and uplink throughput. [Needs Verification]
- [3GPP Evidence] TS 38.331 Section 5.3 is relevant to RRC connection control and readiness. [Needs Verification]
- [3GPP Evidence] TS 38.214 Section 6.1 is relevant to PUSCH scheduling and throughput. [Needs Verification]
- [Inference] P5 does not claim 3GPP feature completeness; it evaluates simulator performance-measurement credibility.

## Limitations
- [Limitation] Current DOE is UL-only; DL throughput remains untested.
- [Limitation] RFsim does not reproduce field RF propagation, mobility, SNR, BLER, MIL, MCL, or SUL coverage behavior.
- [Limitation] Current UE-scale factor is a compose pool and sampled UE measurement design, not necessarily full simultaneous traffic concurrency.
- [Limitation] Current PDCCH/control-channel pressure is proxy-only.
- [Limitation] Throughput gaps require P5 follow-up analysis before being attributed to scheduler, host load, UPF path, iperf behavior, or RFsim resource limits.
- [Limitation] Taguchi L9 supports first-pass screening; it does not fully resolve interaction effects.

## Validity Decision
- Decision: [VALID FOR TREND STUDY]
- Rationale:
  - [Measured] P3 produced a [Strong Dataset].
  - [Measured] P4 generated reproducible plots with simulator-aligned axes.
  - [Measured] Runtime stability was strong: no gNB restart, no UDP loss, no ping loss, and 100% attach/PDU/tunnel/forward ping success.
  - [Paper Evidence] PAPER-06/PAPER-07 provide throughput and latency anchors compatible with RFsim `iperf` and `ping` trend analysis.
  - [Inference] The platform is suitable for directional RedCap RFsim performance experiments.
- Boundary:
  - It is not yet valid for absolute paper-equivalent performance reproduction.

## Recommended Next Work
| Priority | Work Item | Reason |
|---|---|---|
| P5-FU-01 | Investigate sender/receiver throughput gap rows | Required before stronger throughput claims |
| P5-FU-02 | Add DL iperf support | Needed for PAPER-06/PAPER-07 DL comparison |
| P5-FU-03 | Add scheduler/control-channel instrumentation | Needed for PAPER-02 PDCCH blocking claims |
| P5-FU-04 | Add host CPU/memory and container resource capture | Needed to explain throughput collapse or RTT rise |
| P5-FU-05 | Separate simultaneous traffic from sequential sampled validation | Needed to clarify load semantics |
| P5-FU-06 | Add channel/link-level simulator or external link-level study | Needed for PAPER-03/PAPER-04 comparison |
