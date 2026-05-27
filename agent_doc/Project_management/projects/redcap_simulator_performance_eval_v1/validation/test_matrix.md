# RedCap Simulator Performance Validation Matrix

## Validation Legend
- [PASS]: required metric captured and meets the current criterion.
- [PASS_WITH_GAP]: runtime passed, but one comparison or instrumentation field remains assumption-based.
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
| PERF-P08-PWR-001 | PAPER-08 uplink power calculator self-test | Equation (1), Table II coefficients | deterministic model outputs for n41/n78 | [x] |
| PERF-P08-PWR-002 | PAPER-08 power calculator socket integration | newline-delimited JSON request | JSON response with `pue_w`, `segment`, duty-cycle average | [x] |
| PERF-P08-PWR-003 | RFsim UL throughput plus modeled power merge | UL iperf row + `band` + `ptx_dbm` input | throughput, jitter, loss, modeled UE UL power | [PASS_WITH_GAP] |
| PERF-P08-SNR-001 | PAPER-08 Fig.9 UDP DL SNR-proxy sweep | RFsim channelmod model + `noise_power_dB` sweep | DL receiver Mbps, UDP loss, blocked/timeout rows | [PASS_WITH_GAP] |
| PERF-P10-THR-001 | PAPER-10 single-UE UL/DL balance | UE1, UL and DL full-buffer iperf | UL Mbps, DL Mbps, DL/UL ratio, MAC evidence | [TODO] |
| PERF-P10-THR-002 | PAPER-10 multi-UE UL/DL balance | 2 to 3 sampled UEs, UL/DL traffic | per-UE throughput, fairness, restart count | [PASS_WITH_GAP] |
| PERF-P10-LAT-001 | PAPER-10 E2E latency proxy | UE ping to 5GC/ext-dn target | RTT min/avg/max, packet loss | [TODO] |
| PERF-P10-POS-001 | PAPER-10 Good/Fair/Bad position proxy | controlled channel/MCS/SNR proxy where available | throughput drop ratio, MCS/SNR evidence | [BLOCKED_BY_INSTRUMENTATION] |
| PERF-P10-HOST-001 | PAPER-10 host PC sensitivity proxy | same RFsim run under different host/resource budget | throughput, RTT, host CPU/memory | [TODO] |
| PERF-P10-STAB-001 | PAPER-10 multi-UE UL stability stress | 2 to 3 UEs with UL traffic and restart diagnostics | gNB restart count, failures, UE attach/PDU/tunnel | [PASS] |

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

## Extended Matrix References
- PAPER-08 / PAPER-10 extended flow:
  - `validation/paper08_10_extended_test_matrix.md`
- PAPER-10 platform improvement checklist:
  - `validation/paper10_platform_improvement_checklist.md`
- PAPER-08 calculator:
  - `analysis/scripts/p08_uplink_power_calculator.py`
- PAPER-08 Fig.9 UDP SNR-proxy reproduction:
  - `analysis/paper08_fig9_udp_snr_sweep_report.md`
  - `analysis/scripts/p08_fig9_udp_snr_sweep.py`
  - `analysis/data/paper08_fig9_udp_snr_combined_2026-05-27_16-03-00.csv`
  - `analysis/data/paper08_fig9_udp_snr_blocked_2026-05-27_16-03-00.csv`
  - `analysis/plots/paper08_fig9_udp_snr_combined_2026-05-27_16-03-00.png`
- PAPER-10 multi-UE software throughput reproduction:
  - `analysis/paper10_multiue_software_throughput_reproduction_2026-05-26_report.md`
  - `analysis/data/paper10_multiue_raw/paper10_multiue_2026-05-26_17-26-35/paper10_multiue_2026-05-26_17-26-35_results.csv`
  - `analysis/data/paper10_multiue_combination_summary_2026-05-26.csv`
