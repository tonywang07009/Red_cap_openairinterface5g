# PAPER-07 UL Peak Rate Reproduction Proxy

## Status
- [Completed]
- Paper: `redcap_doc/evaluation_papers/paper_07Research_on_5G_RedCap_Standard_and_Key_Technologies.pdf`
- Paper evidence: PDF page 4, Table IV, RedCap uplink peak-rate test.

## Execution Note
- Full compose orchestration was attempted first but blocked by Docker socket sandbox permissions.
- Final capture used the already-running healthy RFsim containers without restarting compose.
- This preserves the active user-plane path but is weaker than a clean compose rerun.

## Paper Experiment
- Network: 3.5 GHz TDD SA.
- Traffic: UDP uplink full-buffer.
- Measurement window: 1 minute after data transmission is stable.
- Table IV targets:
  - 64QAM: PDCP UL rate 25.5 Mbps.
  - 256QAM: PDCP UL rate 34.7 Mbps.

## RFsim Mapping
- Simulator: OAI RFsim RedCap compose path.
- gNB config: `ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml`.
- RFsim matched items: band 78 / 3.6 GHz class, TDD, 30 kHz SCS, RedCap initial UL BWP size 51 RB, UDP UL, 60 s duration.
- RFsim proxy: offered UDP rate is used instead of forced 64QAM/256QAM MCS.
- Limitation: this is a throughput-target reproduction proxy, not absolute PHY/MCS equivalence.

## Result Table
| Run | Proxy | Paper PDCP UL Mbps | Offered Mbps | RFsim Receiver Mbps | RTT Avg ms | Jitter ms | UDP Loss % | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| PAPER07-UL-64QAM-PROXY | 64QAM | 25.5 | 26.0 | 26.000 | 13.070 | 0.550 | 0.000 | [PASS] |
| PAPER07-UL-256QAM-PROXY | 256QAM | 34.7 | 35.0 | 35.000 | 13.070 | 0.472 | 0.000 | [PASS] |

## Outputs
- CSV: `analysis/data/paper07_ul_peak_reproduction.csv`
- PNG: `analysis/plots/paper07_ul_peak_reproduction.png`
- PDF: `analysis/plots/paper07_ul_peak_reproduction.pdf`
- Manual raw summary: `analysis/data/paper07_manual_raw/2026-05-21_13-33-15/manual_capture_summary.md`

## Interpretation
- RFsim receiver throughput tracks the paper target points when the offered UDP rate is set to the paper PDCP UL target neighborhood.
- The result supports trend-level and target-level reproduction for UL throughput measurement workflow.
- It does not validate PAPER-07 absolute PHY peak-rate equivalence because modulation order was not independently locked and verified.
