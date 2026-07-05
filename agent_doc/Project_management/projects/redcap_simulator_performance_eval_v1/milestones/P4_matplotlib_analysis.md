# P4 Matplotlib Analysis

## Milestone Metadata
- Milestone: P4
- Task IDs: P4-T1
- Status: [COMPLETED]

## Purpose
- Generate performance plots whose axes match simulator-observed variables.

## Plot Rules
- Use Python + matplotlib.
- Input data lives under `analysis/data/`.
- Scripts live under `analysis/scripts/`.
- Output figures live under `analysis/plots/`.
- Each figure must state:
  - [X-axis] simulator variable and unit
  - [Y-axis] simulator metric and unit
  - [Scenario]
  - [Source CSV]

## Required Initial Plots
- throughput vs offered rate
- throughput vs UE count
- RTT latency vs UE count
- jitter vs UE count
- packet loss vs UE count

## Acceptance Criteria
- [x] Script can regenerate every plot from CSV.
- [x] Axis labels match simulator logs and units.
- [x] Figures are suitable for Markdown/PDF export.

## P4-T1 Result
- Script:
  - `analysis/scripts/p4_generate_plots.py`
- Input:
  - `analysis/data/p3_runtime_metrics.csv`
- Report:
  - `analysis/p4_matplotlib_plot_report.md`
- Generated figures:
  - `analysis/plots/p4_throughput_vs_offered_rate.png`
  - `analysis/plots/p4_throughput_vs_offered_rate.pdf`
  - `analysis/plots/p4_throughput_vs_total_ues.png`
  - `analysis/plots/p4_throughput_vs_total_ues.pdf`
  - `analysis/plots/p4_rtt_latency_vs_total_ues.png`
  - `analysis/plots/p4_rtt_latency_vs_total_ues.pdf`
  - `analysis/plots/p4_jitter_vs_total_ues.png`
  - `analysis/plots/p4_jitter_vs_total_ues.pdf`
  - `analysis/plots/p4_packet_loss_vs_total_ues.png`
  - `analysis/plots/p4_packet_loss_vs_total_ues.pdf`
  - `analysis/plots/p4_sender_receiver_gap_by_run.png`
  - `analysis/plots/p4_sender_receiver_gap_by_run.pdf`

## Axis Mapping
| Figure | X-axis | Y-axis | Source |
|---|---|---|---|
| throughput vs offered rate | offered rate (Mbit/s) | receiver/sender throughput (Mbit/s) | iperf command + iperf logs |
| throughput vs UE count | total UE compose pool (count) | receiver/sender throughput (Mbit/s) | RFsim runtime factors + iperf logs |
| RTT latency vs UE count | total UE compose pool (count) | RTT avg (ms) | ping logs |
| jitter vs UE count | total UE compose pool (count) | UDP jitter (ms) | iperf receiver logs |
| packet loss vs UE count | total UE compose pool (count) | UDP/ping loss (%) | iperf receiver logs + ping logs |
| sender-receiver gap by run | run ID | sender - receiver throughput (Mbit/s) | derived from parsed iperf logs |

## P4 Observations For P5
- `DOE-L9-03`, `DOE-L9-05`, and `DOE-L9-09` show sender/receiver throughput gaps.
- All rows have UDP loss 0% and gNB restart count 0.
- RTT avg increases in 8 sampled UE rows.
- These plots support RFsim trend analysis, not absolute paper-level equivalence by themselves.

## Verification
- `python3 -m py_compile analysis/scripts/p4_generate_plots.py`: [PASS]
- `python3 analysis/scripts/p4_generate_plots.py`: [PASS]
- PNG outputs are non-empty and reported as valid PNG images.
