# Work Daily - PAPER-07 UL Peak Reproduction

## Scope
- Project: `redcap_simulator_performance_eval_v1`
- Paper: `evaluation_paper/Research_on_5G_RedCap_Standard_and_Key_Technologies.pdf`
- Target: PAPER-07 Table IV uplink peak-rate test.

## Execution
- Selected PAPER-07 because it has explicit UDP uplink full-buffer and 1-minute PDCP UL throughput targets.
- Attempted scripted compose-based reproduction first.
- Compose attempt failed under sandbox with Docker socket permission denial.
- Used safer fallback: current healthy RFsim containers, no compose restart.
- Ran UE1 UDP UL iperf3 from `10.0.0.2` to `192.168.72.135`.

## Results
| Point | Paper PDCP UL Mbps | Offered UDP Mbps | RFsim Receiver Mbps | Jitter ms | UDP Loss % |
|---|---:|---:|---:|---:|---:|
| 64QAM proxy | 25.5 | 26.0 | 26.0 | 0.550 | 0.0 |
| 256QAM proxy | 34.7 | 35.0 | 35.0 | 0.472 | 0.0 |

## Outputs
- CSV: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper07_ul_peak_reproduction.csv`
- Plot PNG: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/plots/paper07_ul_peak_reproduction.png`
- Plot PDF: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/plots/paper07_ul_peak_reproduction.pdf`
- Report: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/paper07_ul_peak_reproduction_report.md`

## Limitation
- This is a throughput-target reproduction proxy.
- It does not prove absolute PAPER-07 PHY/MCS equivalence because current automation did not lock or independently verify 64QAM/256QAM MCS.
