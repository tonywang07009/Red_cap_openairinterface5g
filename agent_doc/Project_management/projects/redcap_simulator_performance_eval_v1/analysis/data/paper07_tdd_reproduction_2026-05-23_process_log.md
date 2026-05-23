# PAPER-07 TDD Reproduction Process Log - 2026-05-23

## Source Paper
- Paper: `evaluation_paper/RedCap_Performance_Analysis_and_Deployment_Strategy_Research.pdf`
- PDF metadata title: `RedCap Performance Analysis and Deployment Strategy Research`
- Extracted paper target: TDD 20MHz 256QAM, 1T2R, UL `34 Mbps`, DL `140 Mbps`.
- FDD paper target exists but was not run in this experiment: 20MHz 256QAM, UL `120 Mbps`, DL `226 Mbps`.

## Runtime Setup
```text
MMTC_TOTAL_UES=29
MMTC_SAMPLE_UES=1
MMTC_IPERF_SAMPLE_UES=1
MMTC_IPERF_ENABLE=1
MMTC_IPERF_UDP=1
MMTC_IPERF_RATE=35M
MMTC_IPERF_DURATION=60
MMTC_FORWARD_PING_MODE=parallel
MMTC_RUN_REVERSE_PING=0
MMTC_PING_COUNT=10
MMTC_GNB_WARMUP=5
MMTC_SLEEP_AFTER_UP=25
MMTC_UE_START_GAP=0
MMTC_PUCCH_COMMON_FALLBACK_BWP0=1
MMTC_PUSCH_256QAM=1
MMTC_PDSCH_256QAM=1
```

## UE Runtime Capability
```text
nrue_recap:
  support_of_redcap_r17: 1
  number_of_rx_redcap_r17: 1
  half_duplex_fdd_type_a_redcap_r17: 1
  pusch_256qam: 1
  pdsch_256qam: 1
```

UE log evidence:
```text
nrue_recap RedCap config: band=n78 RedCap=1 ... PUSCH256QAM=1 PDSCH256QAM=1
```

## Health Check
```text
[SUMMARY] sample=1 running=1 attach=1 pdu=1 tun=1 forward_ping_ok=1 reverse_ping_ok=0 iperf_ul_ok=1 iperf_ul_run=1 gnb_restart=0 failures=0 mode=parallel
```

Ping result:
```text
10 packets transmitted, 10 received, 0% packet loss
rtt min/avg/max/mdev = 2.763/3.904/4.492/0.505 ms
```

## UL 35M iperf Result
Command:
```bash
docker exec rfsim5g-oai-nr-ue1_redcap iperf3 -c 192.168.72.135 -t 60 -B 10.0.0.2 -u -b 35M
```

Raw log:
```text
test_log/compiler_logs/mmtc_smoke_2026-05-23_12-07-00_ue1_iperf3_ul.log
```

Final output:
```text
[  5]   0.00-60.00  sec   250 MBytes  35.0 Mbits/sec  0.000 ms  0/181282 (0%)  sender
[  5]   0.00-60.04  sec   250 MBytes  35.0 Mbits/sec  0.392 ms  0/181282 (0%)  receiver
```

Active gNB ULSCH evidence:
```text
UE 6a8c: ulsch_rounds 156097/0/0/0, ulsch_errors 0, ulsch_DTX 0,
BLER 0.00000 MCS (1) 27 (Qm 8 deltaMCS 0 dB) NPRB 106 SNR 50.5 dB CCE fail 0
```

## DL 141M Reverse iperf Result
Command:
```bash
docker exec rfsim5g-oai-nr-ue1_redcap iperf3 -c 192.168.72.135 -B 10.0.0.2 -t 60 -u -b 141M -R
```

Final output:
```text
[  5]   0.00-60.09  sec  1010 MBytes   141 Mbits/sec  0.000 ms  0/0 (0%)  sender
[  5]   0.00-60.00  sec  1009 MBytes   141 Mbits/sec  0.039 ms  436/731378 (0.06%)  receiver
```

Active gNB DLSCH evidence:
```text
UE 6a8c: dlsch_rounds 41957/0/0/0, dlsch_errors 0, pucch0_DTX 0,
BLER 0.00000 MCS (1) 27 CCE fail 0
```

## Interpretation
- UL passed the paper TDD target: measured `35.0 Mbps` vs paper `34 Mbps`.
- DL passed the paper TDD target: measured `141 Mbps` vs paper `140 Mbps`.
- UL modulation evidence passed: active gNB stats showed `MCS (1)` and `Qm 8`.
- DL modulation evidence passed by table selection: active gNB stats showed DLSCH `MCS (1)`.
- This run validates the TDD portion only. FDD UL/DL remains a separate project task.
