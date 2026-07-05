# P2 Taguchi Experiment Design

## Milestone Metadata
- Milestone: P2
- Task IDs: P2-T1, P2-T2
- Status: [COMPLETED]

## Purpose
- Use [Taguchi DOE] to reduce the number of RFsim runs while still covering major performance factors.

## Output
- DOE design: `validation/taguchi_doe_matrix.md`
- CSV run matrix: `analysis/data/p2_taguchi_l9_run_matrix.csv`

## Candidate Factors
- [UE scale]: 16, 32, 56 UEs.
- [Traffic rate]: 10M, 50M, 85M UDP uplink.
- [Validation sample depth]: 1, 4, 8 sampled UEs.
- [Dummy column]: D1, D2, D3 for residual/error visibility.
- [Excluded from first DOE]: DL iperf, SNR/BLER/MIL/MCL, low-power mode, and BWP/CORESET case.

## Candidate Responses
- uplink throughput
- RTT latency
- jitter
- packet loss
- attach/PDU/tunnel success ratio
- gNB restart count

## Acceptance Criteria
- [x] Factors and levels are justified by P1 paper evidence and actual simulator knobs.
- [x] Orthogonal array choice is documented.
- [x] Run matrix is executable by existing scripts or explicitly lists missing automation.
- [x] Limitations of Taguchi interaction coverage are stated.
