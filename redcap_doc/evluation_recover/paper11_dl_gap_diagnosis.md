# PAPER-11 DL Gap Diagnosis

## Question
- [Observed]: PAPER-07 previously reached DL `141 Mbps`.
- [Observed]: PAPER-11 far-gate run reached DL receiver `32.7 Mbps` when offered `68M`.
- [Question]: why did the previous DL peak not repeat?

## Short Answer
- [Primary Cause]: the two runs used different [experiment profiles].
- [PAPER-07 Profile]: single UE peak-rate reproduction, `PDSCH256QAM=1`, DLSCH `MCS (1) 27`, `60 s` UDP reverse iperf.
- [PAPER-11 Profile]: real-network service-gate reproduction on already-running containers, `10 s` UDP reverse iperf, no explicit re-application of PAPER-07 `PDSCH256QAM=1`, and no DLSCH MCS evidence captured in the run.
- [PAPER-10 Note]: the `144.675 Mbps` number is a 3-UE aggregate DL receiver result under high loss, not a single-UE clean `141 Mbps` pass.
- [Current Runtime Evidence]: after the PAPER-11 run, UE1 `/tmp/nr-ue-mmtc.yaml` showed `pusch_256qam: 0` and `pdsch_256qam: 0`; this confirms it was not running the PAPER-07 256QAM peak-rate profile.

## Evidence Comparison
| Item | PAPER-07 DL 141M Pass | PAPER-11 DL 68M Gap |
|---|---|---|
| Goal | peak-rate reproduction | IoT service-gate reproduction |
| UE Count | single measured UE | single UE |
| Duration | `60 s` | `10 s` in first far-gate run |
| DL Offered Rate | `141M` | `68M` |
| Receiver Result | `141 Mbps` | `32.7 Mbps` |
| Loss | `0.060%` | `0.63%` |
| Capability Profile | `PDSCH256QAM=1` | not explicitly applied by `paper11_iperf_live_demo.sh` |
| Current UE YAML | `pdsch_256qam: 1` during PAPER-07 retest | `pdsch_256qam: 0` observed after PAPER-11 |
| MAC Evidence | DLSCH `MCS (1) 27` | not captured |
| Interpretation | [Peak-rate PASS] | [Service-gate PASS_WITH_GAP] |

## Detailed Cause
- [Capability State]:
  - PAPER-07 intentionally enabled `MMTC_PDSCH_256QAM=1`.
  - PAPER-07 verified DLSCH `MCS (1) 27`, which is the local evidence that DL 256QAM table was selected.
  - PAPER-11 used the currently running RFsim containers and did not restart/apply the PAPER-07 256QAM profile before traffic.
- [Measurement Objective]:
  - PAPER-07 used a peak-rate target: prove that the simulator can hit `140 Mbps` DL when configured for the paper's 256QAM point.
  - PAPER-11 used application service gates from a real-network paper: industrial, video, wearable, and far-point thresholds.
- [Duration / Warm-Up]:
  - PAPER-11 `10 s` far-gate run had a slow DL ramp in the first few seconds.
  - A short average penalizes the final result more than the PAPER-07 `60 s` window.
- [Aggregate Confusion]:
  - PAPER-10's `144.675 Mbps` DL was an aggregate across `UE1+UE2+UE3`.
  - Per-UE PAPER-10 DL was about `48 Mbps` with about `61.6%` loss because the offered load was intentionally saturating.

## Correct Retest To Prove The Difference
```bash
# 1. Apply PAPER-07 peak-rate profile.
bash redcap_interface/mmtc.menu.bash
# choose:
# 16) Run PAPER-07 reproduction bundle

# 2. Or manually run PAPER-11 after enabling its panel.
P11_PANEL=1 P11_MODE=both P11_UL_RATE=17M P11_DL_RATE=68M P11_DURATION=60 \
  bash redcap_interface/paper11_iperf_live_demo.sh
```

## Decision Rule
- [If DLSCH shows `MCS (1) 27` and DL still stays near `32 Mbps`]:
  - investigate current gNB config, PRB profile, RFsim channel model, CPU pressure, and iperf reverse path.
- [If DLSCH does not show `MCS (1)`]:
  - this is not the same condition as the PAPER-07 `141 Mbps` pass.
- [If 60 s PAPER-11 DL improves but not to `68 Mbps`]:
  - classify as [PAPER-11 service-gate PASS_WITH_GAP], not as a platform regression.
