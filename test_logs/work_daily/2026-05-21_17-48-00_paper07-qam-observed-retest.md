# Work Daily - PAPER-07 QAM Observed Retest

## Scope
- Project: `redcap_simulator_performance_eval_v1`
- Paper: `evaluation_paper/Research_on_5G_RedCap_Standard_and_Key_Technologies.pdf`
- Target: distinguish PAPER-07 64QAM and 256QAM uplink points using observed gNB MAC stats.

## Method
- Reused active RFsim containers because full compose restart was blocked by Docker socket sandbox permissions earlier.
- Ran UE1 UDP UL iperf3 for 60 seconds per point.
- Sampled `rfsim5g-oai-gnb_redcap:/opt/oai-gnb/nrMAC_stats.log` while traffic was active.
- Acceptance for actual QAM:
  - 64QAM: `Qm 6`, normally with MCS table `0`.
  - 256QAM: `Qm 8`, normally with MCS table `1`.

## Results
| Point | Offered Mbps | Receiver Mbps | Observed MCS table | Observed MCS | Observed Qm | Verdict |
|---|---:|---:|---:|---:|---:|---|
| 64QAM point | 26.0 | 26.0 | 0 | 28 | 6 | Match |
| 256QAM point | 35.0 | 35.0 | 0 | 28 | 6 | Mismatch; still 64QAM |

## Interpretation
- The platform successfully exercised 64QAM during the 26M point.
- The platform did not exercise true 256QAM during the 35M point.
- The previous 35M result should be interpreted as throughput-target reproduction, not 256QAM reproduction.
- A true 256QAM retest requires enabling UE PUSCH 256QAM capability and PUSCH `mcs_Table=qam256`, then confirming `MCS (1)` and `Qm 8` in gNB MAC stats.

## Outputs
- CSV: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper07_qam_observed_retest.csv`
- Plot PNG: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/plots/paper07_qam_observed_retest.png`
- Plot PDF: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/plots/paper07_qam_observed_retest.pdf`
- Report: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/paper07_qam_observed_retest_report.md`
