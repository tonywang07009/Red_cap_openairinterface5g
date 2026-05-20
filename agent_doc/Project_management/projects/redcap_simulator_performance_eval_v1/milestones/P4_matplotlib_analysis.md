# P4 Matplotlib Analysis

## Milestone Metadata
- Milestone: P4
- Task IDs: P4-T1
- Status: [NOT STARTED]

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
- [ ] Script can regenerate every plot from CSV.
- [ ] Axis labels match simulator logs and units.
- [ ] Figures are suitable for Markdown/PDF export.
