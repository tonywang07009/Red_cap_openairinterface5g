# P1 Literature Metric Baseline

## Milestone Metadata
- Milestone: P1
- Task IDs: P1-T1, P1-T2
- Status: [COMPLETED]

## Purpose
- Extract only the paper evidence needed to define simulator performance expectations.
- Convert paper graphs/tables into a compact metric map for RFsim validation.

## Source Papers
- See `literature/paper_index.md`.
- Extracted baseline: `literature/p1_metric_baseline.md`.

## Required Output
- Paper metric table:
  - [Paper]
  - [Metric]
  - [Scenario]
  - [X-axis]
  - [Y-axis]
  - [Simulator-equivalent signal]
  - [Extraction confidence]
- Candidate comparable metrics:
  - throughput vs offered load
  - latency vs UE count
  - packet loss vs UE count
  - control channel blocking probability vs load
  - coverage / reliability indicators where RFsim can provide a proxy

## Acceptance Criteria
- [x] Each selected paper has at least one extracted metric or is marked [Not Directly Comparable].
- [x] Every claimed reference value points to a paper file and page/figure/table when available.
- [x] No result is treated as 3GPP normative behavior unless mapped to a local spec note or TS clause.
