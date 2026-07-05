# 2026-05-28 PAPER-11 Table 3 Peak-Rate Proxy

## Work Completed
- [Runner]: added `redcap_interface/paper11_table3_peak_reproduction.sh`.
- [Menu]: added option `20` in `redcap_interface/redcap_runtime_menu.sh`.
- [Manual]: added `redcap_doc/evluation_recover/paper11_table3_2p1g_peak_rate_step_by_step.md`.
- [Evidence]: stored raw iperf/MAC logs under `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper11_table3_raw/paper11_table3_2026-05-28_10-40/`.

## Run Summary
| Test | Target | Receiver | Loss | Status |
|---|---:|---:|---:|---|
| UL 64QAM | 90 Mbps | 89.9 Mbps | 0% | PASS_WITH_GAP |
| DL 64QAM | 169.5 Mbps | 170 Mbps | 0.053% | PASS |
| DL 256QAM | 226 Mbps | 226 Mbps | 0.058% | PASS |

## Evidence Notes
- [UL 64QAM MAC]: `MCS (0) 28`, `Qm 6`, `NPRB 18`, `SNR 51.0 dB`.
- [DL 64QAM MAC]: `MCS (0) 28`, `BLER 0.00000`.
- [DL 256QAM MAC]: `MCS (1) 27`, `BLER 0.00000`.

## Limitation
- [Target-Rate Proxy]: Paper11 Table 3 is 2.1G/20M/FDD/1T2R; this run used the stable RedCap band78/51PRB/30k/TDD RFsim path.
