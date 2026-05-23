# PAPER-07 TDD Reproduction Report - 2026-05-23

## Scope
- [Status]: Completed.
- [Paper]: `evaluation_paper/RedCap_Performance_Analysis_and_Deployment_Strategy_Research.pdf`.
- [Paper Evidence]: PDF page 3 describes RedCap simulation parameters; PDF page 4 table lists RedCap peak rates by duplex/BWP.
- [Reproduction Scope]: TDD only.
- [Deferred Scope]: FDD UL/DL, because the current RFsim scenario is TDD n78.

## Source Correction
- Earlier working reports used a different filename label for PAPER-07.
- This run uses the user-confirmed PAPER-07 file: `RedCap_Performance_Analysis_and_Deployment_Strategy_Research.pdf`.
- The paper's TDD target used here is: 20MHz 256QAM, 1T2R, UL `34 Mbps`, DL `140 Mbps`.

## Experiment Design
| Factor | Setting | Reason |
|---|---|---|
| Duplex | TDD | Matches the currently runnable RFsim n78 scenario |
| BWP / bandwidth target | Paper 20MHz target, simulator `N_RB_DL=106` | Simulator is not a perfect 20MHz channel clone; throughput target is used as the validation anchor |
| Modulation | 256QAM | Paper TDD row is `20MHz (256QAM)` |
| UE sample | UE1 | Single measured UE for peak-rate reproduction |
| Total UE services | 29 | Required by the existing mMTC smoke script; only UE1 was sampled/measured |
| UL offered rate | 35M UDP | Slightly above paper UL target of 34Mbps |
| DL offered rate | 141M UDP reverse mode | Slightly above paper DL target of 140Mbps |
| Duration | 60s | Stable enough for full-buffer iperf comparison |
| Evidence gate | gNB `nrMAC_stats.log` | Prevents accepting throughput without MCS-table evidence |

## Step-by-Step Execution
1. Extracted the correct paper target from `RedCap_Performance_Analysis_and_Deployment_Strategy_Research.pdf`.
2. Restarted RFsim TDD with the existing mMTC validation script.
3. Enabled both `MMTC_PUSCH_256QAM=1` and `MMTC_PDSCH_256QAM=1`.
4. Confirmed UE runtime YAML contained both `pusch_256qam: 1` and `pdsch_256qam: 1`.
5. Confirmed UE attach, PDU session, tunnel creation, ping, and zero gNB restart.
6. Ran UL 35M UDP iperf for 60 seconds.
7. Sampled active gNB ULSCH stats during UL traffic.
8. Ran DL 141M UDP reverse iperf for 60 seconds.
9. Sampled active gNB DLSCH stats during DL traffic.
10. Wrote CSV, process log, report, and plot artifacts.

## Result Table
| Direction | Paper Target | Offered Rate | Measured Receiver | Jitter | UDP Loss | MAC Evidence | Verdict |
|---|---:|---:|---:|---:|---:|---|---|
| UL | 34 Mbps | 35M | 35.0 Mbps | 0.392 ms | 0.000% | `MCS (1) 27`, `Qm 8`, `NPRB 106` | PASS |
| DL | 140 Mbps | 141M | 141.0 Mbps | 0.039 ms | 0.060% | DLSCH `MCS (1) 27` | PASS |

## Runtime Health
```text
[SUMMARY] sample=1 running=1 attach=1 pdu=1 tun=1 forward_ping_ok=1 reverse_ping_ok=0 iperf_ul_ok=1 iperf_ul_run=1 gnb_restart=0 failures=0 mode=parallel
```

Ping readiness:
```text
10 packets transmitted, 10 received, 0% packet loss
rtt min/avg/max/mdev = 2.763/3.904/4.492/0.505 ms
```

## Evidence Files
- CSV: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper07_tdd_reproduction_2026-05-23.csv`
- Process log: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper07_tdd_reproduction_2026-05-23_process_log.md`
- Plot PNG: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/plots/paper07_tdd_reproduction_2026-05-23.png`
- Plot PDF: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/plots/paper07_tdd_reproduction_2026-05-23.pdf`
- UL raw log: `test_log/compiler_logs/mmtc_smoke_2026-05-23_12-07-00_ue1_iperf3_ul.log`
- UE log: `test_log/compiler_logs/mmtc_smoke_2026-05-23_12-07-00_ue1_docker.log`
- Ping log: `test_log/compiler_logs/mmtc_smoke_2026-05-23_12-07-00_ue1_ping.log`

## Limitations
- This is a TDD RFsim reproduction, not a field-channel reproduction.
- RFsim does not reproduce paper base-station power, UE power, cell distance, or RSRP/SINR distribution exactly.
- The paper TDD target is 20MHz, while this simulator runtime reports `N_RB_DL=106`; therefore the result is a target-rate reproduction with MAC evidence, not a one-to-one RF/channel parameter clone.
- DL gNB stats expose the MCS table as `MCS (1)` but do not print `Qm`; UL prints both `MCS (1)` and `Qm 8`.
- FDD values in the paper are not validated in this run.

## Conclusion
- The current TDD RFsim RedCap simulator can reproduce the selected PAPER-07 TDD 20MHz 256QAM peak-rate targets at the iperf throughput level.
- The UL result is stronger than throughput-only evidence because active gNB stats showed ULSCH table 1 and `Qm 8`.
- The DL result passed throughput and DLSCH table evidence via `MCS (1)`.
- Final status: [TDD PAPER-07 reproduction passed], [FDD remains pending].
