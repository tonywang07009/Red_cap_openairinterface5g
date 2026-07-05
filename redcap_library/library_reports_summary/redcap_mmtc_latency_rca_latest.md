# RedCap mMTC Latency RCA
- Timestamp: 2026-04-28_12-40-05
- Log Dir: test_log/compiler_logs

## Stage Summary
- mmtc_stage_scan_2026-04-28_12-40-05_summary.log: [STAGE] ue=50 status=PASS rc=0 [SUMMARY] sample=50 running=50 attach=50 pdu=50 tun=50 forward_ping_ok=50 reverse_ping_ok=0 iperf_ul_ok=1 iperf_ul_run=1 gnb_restart=0 failures=0 mode=parallel
- mmtc_stage_scan_2026-04-28_12-40-05_ue50.log: [SUMMARY] sample=50 running=50 attach=50 pdu=50 tun=50 forward_ping_ok=50 reverse_ping_ok=0 iperf_ul_ok=1 iperf_ul_run=1 gnb_restart=0 failures=0 mode=parallel

## Ping RTT
- Samples: 50
- Avg RTT ms: 808.114
- Min RTT ms: 83.536
- P50 RTT ms: 830.164
- P95 RTT ms: 1099.805
- Max RTT ms: 1210.992

## TCP iperf3
| Log | Sender Mbps | Receiver Mbps | Error |
|-----|-------------|---------------|-------|
| mmtc_smoke_2026-04-28_12-40-05_ue1_iperf3_ul.log | 20.000 | 20.000 |  |

## UE Sim-Time Drift
| Log | Samples | Wall Seconds | Sim Seconds | Wall/Sim Ratio |
|-----|---------|--------------|-------------|----------------|
| mmtc_smoke_2026-04-28_12-40-05_ue47_docker.log | 3 | 24.513 | 2.560 | 9.575 |
| mmtc_smoke_2026-04-28_12-40-05_ue49_docker.log | 3 | 24.513 | 2.560 | 9.575 |
| mmtc_smoke_2026-04-28_12-40-05_ue48_docker.log | 3 | 24.513 | 2.560 | 9.575 |
| mmtc_smoke_2026-04-28_12-40-05_ue50_docker.log | 3 | 24.513 | 2.560 | 9.575 |
| mmtc_smoke_2026-04-28_12-40-05_ue40_docker.log | 4 | 36.423 | 3.840 | 9.485 |
| mmtc_smoke_2026-04-28_12-40-05_ue41_docker.log | 4 | 36.423 | 3.840 | 9.485 |
| mmtc_smoke_2026-04-28_12-40-05_ue43_docker.log | 4 | 36.423 | 3.840 | 9.485 |
| mmtc_smoke_2026-04-28_12-40-05_ue44_docker.log | 4 | 36.423 | 3.840 | 9.485 |
| mmtc_smoke_2026-04-28_12-40-05_ue42_docker.log | 4 | 36.422 | 3.840 | 9.485 |
| mmtc_smoke_2026-04-28_12-40-05_ue46_docker.log | 4 | 36.422 | 3.840 | 9.485 |

## RCA Hint
- High RTT with low TCP receiver Mbps and low retransmission count points to scheduling latency or RFsim process-time drift.
- A high Wall/Sim Ratio indicates the UE softmodem is advancing radio frames slower than real time.
- If stop-quiesce restores TCP throughput, idle RFsim UE processes are still consuming enough host/RFsim time to affect the active UE.
