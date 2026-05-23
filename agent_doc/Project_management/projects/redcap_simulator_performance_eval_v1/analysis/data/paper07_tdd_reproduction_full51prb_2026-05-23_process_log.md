# PAPER-07 TDD Full-Carrier 51PRB Process Log

## Scope
- Paper: `evaluation_paper/RedCap_Performance_Analysis_and_Deployment_Strategy_Research.pdf`
- Target: TDD 20 MHz / 51 PRB / 30 kHz SCS style reproduction.
- Purpose: make `dl_carrierBandwidth` and `ul_carrierBandwidth` equal 51, then rerun PAPER-07 UL/DL.

## Configuration
- Baseline 106PRB file kept unchanged:
  - `ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml`
- Full-carrier 51PRB file:
  - `ci-scripts/conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml`
- Full-carrier 51PRB synchronized values:
  - `bwpSize: 51`
  - `dl_absoluteFrequencyPointA: 640564`
  - `dl_carrierBandwidth: 51`
  - `ul_carrierBandwidth: 51`
  - `initialDLBWPcontrolResourceSetZero: 12`
  - `initialDLBWPControlResourceSetZero_r17: 12`
- UE synchronized launch values:
  - `MMTC_N_RB_DL=51`
  - `MMTC_RF_FREQ=3617640000`
  - `MMTC_SSB_START=238`
  - final UE option: `-E --rfsim -r 51 --numerology 1 -C 3617640000 --ssb 238`

## UL Run
- Command profile:
  - `GNB_REDCAP_CONFIG=/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml`
  - `MMTC_N_RB_DL=51`
  - `MMTC_RF_FREQ=3617640000`
  - `MMTC_SSB_START=238`
  - `MMTC_TOTAL_UES=29`
  - `MMTC_SAMPLE_UES=1`
  - `MMTC_IPERF_ENABLE=1`
  - `MMTC_IPERF_UDP=1`
  - `MMTC_IPERF_RATE=35M`
  - `MMTC_IPERF_DURATION=60`
  - `MMTC_PUSCH_256QAM=1`
  - `MMTC_PDSCH_256QAM=1`
- Smoke timestamp:
  - `mmtc_smoke_2026-05-23_16-28-19`
- Attach/PDU/TUN:
  - `attach=1`
  - `pdu=1`
  - `tun=1`
- gNB restart:
  - `gnb_restart=0`
- Ping:
  - 10 transmitted, 10 received, 0% packet loss
  - RTT min/avg/max/mdev = 1.960/2.795/3.817/0.539 ms
- UL iperf receiver:
  - throughput: 35.0 Mbps
  - jitter: 0.380 ms
  - loss: 0/181282 (0%)

## DL Run
- Server:
  - `docker exec oai-ext-dn sh -c 'pids=$(pidof iperf3 2>/dev/null || true); [ -z "$pids" ] || kill $pids; iperf3 -s -D'`
- Client:
  - `docker exec rfsim5g-oai-nr-ue1_redcap iperf3 -c 192.168.72.135 -B 10.0.0.2 -t 60 -u -b 141M -R`
- DL iperf receiver:
  - throughput: 141 Mbps
  - jitter: 0.025 ms
  - loss: 410/731293 (0.056%)

## Runtime Evidence
- gNB container YAML:
  - `bwpSize: 51`
  - `dl_absoluteFrequencyPointA: 640564`
  - `dl_carrierBandwidth: 51`
  - `ul_carrierBandwidth: 51`
  - `initialDLBWPcontrolResourceSetZero: 12`
- UE container environment:
  - `MMTC_N_RB_DL=51`
  - `MMTC_RF_FREQ=3617640000`
  - `MMTC_SSB_START=238`
  - `USE_ADDITIONAL_OPTIONS=-E --rfsim -r 51 --numerology 1 ... -C 3617640000 --ssb 238 ...`

## Interpretation
- The previous full-carrier 51 attempt failed because UE still used 106PRB RF assumptions.
- After aligning gNB PointA/CORESET0 and UE `-r`/RF/SSB parameters, full-carrier 51PRB attach and PAPER-07 throughput validation pass.
