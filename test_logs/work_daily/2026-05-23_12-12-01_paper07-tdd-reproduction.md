# Work Daily - PAPER-07 TDD Reproduction

## Task
- Reproduce the TDD portion of `evaluation_paper/RedCap_Performance_Analysis_and_Deployment_Strategy_Research.pdf`.

## Execution
- Restarted RFsim through `ci-scripts/redcap_mmtc_smoke_validation.sh`.
- Enabled `MMTC_PUSCH_256QAM=1`.
- Enabled `MMTC_PDSCH_256QAM=1`.
- Ran UL 35M UDP iperf for 60 seconds.
- Ran DL 141M UDP reverse iperf for 60 seconds.
- Sampled active gNB MAC stats during UL and DL traffic.

## Results
- UL receiver throughput: `35.0 Mbps`, paper target `34 Mbps`.
- UL jitter/loss: `0.392 ms`, `0%`.
- UL MAC evidence: `MCS (1) 27`, `Qm 8`, `NPRB 106`.
- DL receiver throughput: `141 Mbps`, paper target `140 Mbps`.
- DL jitter/loss: `0.039 ms`, `0.06%`.
- DL MAC evidence: DLSCH `MCS (1) 27`.
- Runtime health: `failures=0`, `gnb_restart=0`.

## Artifacts
- `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/paper07_tdd_reproduction_2026-05-23_report.md`
- `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper07_tdd_reproduction_2026-05-23.csv`
- `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper07_tdd_reproduction_2026-05-23_process_log.md`
- `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/scripts/p7_tdd_reproduction_20260523_plot.py`
