# PAPER-07 TDD UL iperf Process Log

## Source
- Scenario: TDD RedCap RFsim
- Direction: UL
- UE: `rfsim5g-oai-nr-ue1_redcap`
- UE tunnel IP: `10.0.0.2`
- Server: `oai-ext-dn`
- Server IP: `192.168.72.135`
- Primary raw source: `redcap_library/library_runtime_probe/paper07_tdd_ul_iperf_256qam_final.log`

## Run Summary
| Run ID | Timestamp | Offered Rate | PUSCH 256QAM Enabled | Sender Mbps | Receiver Mbps | Jitter ms | Lost / Total | UDP Loss % | Active gNB ULSCH Evidence | Raw Interval Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| PAPER07-UL-64QAM-PROXY | 2026-05-21_13-33-15 | 26M | 0 | 26.0 | 26.0 | 0.550 | 0 / 134667 | 0.000 | Not independently captured in this proxy run | Summary only |
| PAPER07-QAM-64-OBSERVED | 2026-05-21_17-43-00 | 26M | 0 | 26.0 | 26.0 | 0.562 | 0 / not preserved | 0.000 | `MCS (0) 28`, `Qm 6`, `NPRB 35..106` | Summary only |
| PAPER07-QAM-256-OBSERVED | 2026-05-21_17-45-00 | 35M | 0 | 35.0 | 35.0 | 0.670 | 0 / not preserved | 0.000 | `MCS (0) 28`, `Qm 6`, expected 256QAM not reached | Summary only |
| PAPER07-QAM-256-TRUE | 2026-05-21_18-04-58 | 35M | 1 | 35.0 | 35.0 | 0.326 | 0 / 181282 | 0.000 | `MCS (1) 27`, `Qm 8`, `NPRB 106` | Full raw interval preserved |

## Data Integrity Notes
- The 2026-05-21_13-33-15 manual proxy run preserved only the final iperf summary table.
- The 2026-05-21_17-43-00 and 2026-05-21_17-45-00 observed retest rows preserved summary metrics and gNB evidence, but not the full per-second iperf interval output.
- The 2026-05-21_18-04-58 true 256QAM run preserved the complete UL iperf output and is the authoritative raw process trace for PAPER-07 TDD UL 256QAM.

## Summary-Only Record: PAPER07-UL-64QAM-PROXY
```text
Source:
agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper07_manual_raw/2026-05-21_13-33-15/manual_capture_summary.md

Command:
docker exec rfsim5g-oai-nr-ue1_redcap iperf3 -c 192.168.72.135 -t 60 -B 10.0.0.2 -u -b 26M

Captured final summary:
Sender:   26.0 Mbits/sec
Receiver: 26.0 Mbits/sec
Jitter:   0.550 ms
Loss:     0/134667 (0%)
Datagrams: 134667

Limitation:
Full per-second iperf interval output was not preserved for this run.
```

## Summary-Only Record: PAPER07-UL-256QAM-PROXY
```text
Source:
agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper07_manual_raw/2026-05-21_13-33-15/manual_capture_summary.md

Command:
docker exec rfsim5g-oai-nr-ue1_redcap iperf3 -c 192.168.72.135 -t 60 -B 10.0.0.2 -u -b 35M

Captured final summary:
Sender:   35.0 Mbits/sec
Receiver: 35.0 Mbits/sec
Jitter:   0.472 ms
Loss:     0/181283 (0%)
Datagrams: 181283

Limitation:
Full per-second iperf interval output was not preserved for this run.
```

## Summary-Only Record: PAPER07-QAM-64-OBSERVED
```text
Source:
agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper07_qam_observed_retest.csv

Timestamp: 2026-05-21_17-43-00
Command intent:
UL iperf3, 60 seconds, UDP, offered rate 26M, UE source IP 10.0.0.2, server 192.168.72.135.

Captured final summary:
Sender:   26.0 Mbits/sec
Receiver: 26.0 Mbits/sec
Jitter:   0.562 ms
Loss:     0.0%
RTT avg:  12.141 ms

Active gNB evidence:
ULSCH MCS table 0, MCS index 28, Qm 6, NPRB 35..106, SNR 50.0..51.0 dB.

Verdict:
MATCH_64QAM

Limitation:
Full per-second iperf interval output was not preserved for this run.
```

## Summary-Only Record: PAPER07-QAM-256-OBSERVED
```text
Source:
agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper07_qam_observed_retest.csv

Timestamp: 2026-05-21_17-45-00
Command intent:
UL iperf3, 60 seconds, UDP, offered rate 35M, UE source IP 10.0.0.2, server 192.168.72.135.

Captured final summary:
Sender:   35.0 Mbits/sec
Receiver: 35.0 Mbits/sec
Jitter:   0.670 ms
Loss:     0.0%
RTT avg:  12.141 ms

Active gNB evidence:
ULSCH MCS table 0, MCS index 28, Qm 6, NPRB 35..106, SNR 50.5..51.0 dB.

Verdict:
MISMATCH_EXPECTED_256QAM

Limitation:
Full per-second iperf interval output was not preserved for this run.
This run did not prove true 256QAM because active gNB stats stayed at table 0 / Qm 6.
```

## Raw iperf Output: PAPER07-QAM-256-TRUE
```text
# collected_at=2026-05-21T18:06:21+08:00
# direction=UL
# ue=1
# container=rfsim5g-oai-nr-ue1_redcap
# target=192.168.72.135
# ue_ipv4=10.0.0.2
# command: docker exec rfsim5g-oai-nr-ue1_redcap iperf3 -c 192.168.72.135 -t 60 -B 10.0.0.2 -u -b 35M
Connecting to host 192.168.72.135, port 5201
[  5] local 10.0.0.2 port 53950 connected to 192.168.72.135 port 5201
[ ID] Interval           Transfer     Bitrate         Total Datagrams
[  5]   0.00-1.00   sec  4.17 MBytes  35.0 Mbits/sec  3019
[  5]   1.00-2.00   sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]   2.00-3.00   sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]   3.00-4.00   sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]   4.00-5.00   sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]   5.00-6.00   sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]   6.00-7.00   sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]   7.00-8.00   sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]   8.00-9.00   sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]   9.00-10.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  10.00-11.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  11.00-12.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  12.00-13.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  13.00-14.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  14.00-15.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  15.00-16.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  16.00-17.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  17.00-18.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  18.00-19.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  19.00-20.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  20.00-21.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  21.00-22.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  22.00-23.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  23.00-24.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  24.00-25.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  25.00-26.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  26.00-27.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  27.00-28.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  28.00-29.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  29.00-30.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  30.00-31.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  31.00-32.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  32.00-33.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  33.00-34.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  34.00-35.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  35.00-36.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  36.00-37.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  37.00-38.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  38.00-39.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  39.00-40.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  40.00-41.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  41.00-42.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  42.00-43.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  43.00-44.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  44.00-45.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  45.00-46.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  46.00-47.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  47.00-48.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  48.00-49.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  49.00-50.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  50.00-51.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  51.00-52.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  52.00-53.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  53.00-54.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  54.00-55.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  55.00-56.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  56.00-57.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  57.00-58.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
[  5]  58.00-59.00  sec  4.17 MBytes  35.0 Mbits/sec  3022
[  5]  59.00-60.00  sec  4.17 MBytes  35.0 Mbits/sec  3021
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-60.00  sec   250 MBytes  35.0 Mbits/sec  0.000 ms  0/181282 (0%)  sender
[  5]   0.00-60.04  sec   250 MBytes  35.0 Mbits/sec  0.326 ms  0/181282 (0%)  receiver

iperf Done.
```

## gNB Evidence: PAPER07-QAM-256-TRUE
```text
UE 6cd3: ulsch_rounds 27059/0/0/0, ulsch_errors 0, ulsch_DTX 0,
BLER 0.00000 MCS (1) 27 (Qm 8 deltaMCS 0 dB) NPRB 106 SNR 50.0 dB CCE fail 0
```

## Interpretation
- PAPER07-QAM-64-OBSERVED is the usable 64QAM UL reference because gNB stats matched table 0 / Qm 6.
- PAPER07-QAM-256-OBSERVED reached the 35M offered-rate target but did not prove 256QAM because gNB stats stayed at table 0 / Qm 6.
- PAPER07-QAM-256-TRUE is the valid true 256QAM UL run because UE PUSCH 256QAM was enabled and active gNB stats showed table 1 / Qm 8.
