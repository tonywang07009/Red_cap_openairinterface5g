# Paper-10 Multi-UE Software Throughput Tutorial

[English](./paper10_multiue_software_throughput_tutorial.en.md) | [繁體中文](./paper10_multiue_software_throughput_tutorial.zh-TW.md)

## Goal

- Reproduce the Paper-10 multi-UE throughput method on OAI RFsim.
- Local scope: OAI-RAN, OAI CN5G, OAI nrUE containers, 3 active UEs.
- Classification: [PASS_WITH_GAP] proxy because Paper-10 uses OTA SDR, Open5GS, and COTS devices.

## Inputs

| Item | Value |
|---|---|
| Band | n78-like RFsim profile |
| Bandwidth | 106 PRB at 30 kHz SCS, about 40 MHz |
| UEs | UE1, UE2, UE3 |
| Traffic | iperf3 UDP, 180 s |
| Historical report | `paper10_multiue_software_throughput_reproduction_2026-05-26_report.md` |

## Procedure

1. Start a 3-UE RFsim topology:

```bash
GNB_REDCAP_CONFIG=/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml \
MMTC_N_RB_DL=106 \
MMTC_RF_FREQ=3630360000 \
MMTC_SSB_START=144 \
MMTC_TOTAL_UES=29 \
MMTC_SAMPLE_UES="1 2 3" \
MMTC_IPERF_ENABLE=0 \
MMTC_FORWARD_PING_MODE=parallel \
MMTC_RUN_REVERSE_PING=0 \
MMTC_PUCCH_COMMON_FALLBACK_BWP0=1 \
MMTC_REDCAP_ENABLE=0 \
bash redcap_interface/redcap_mmtc_smoke_validation.sh
```

2. Confirm readiness:

```text
sample=3
running=3
attach=3
pdu=3
tun=3
forward_ping_ok=3
gnb_restart=0
failures=0
```

3. Run concurrent UL/DL iperf:

```bash
python3 agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/scripts/p10_multiue_iperf_runner.py \
  --ues 1,2,3 \
  --direction both \
  --duration 180 \
  --protocol udp \
  --ul-rate 35M \
  --dl-rate 141M \
  --output-dir agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper10_multiue_raw \
  --limitation-note "RFsim/OAI-CN/OAI-nrUE proxy; paper uses Open5GS, OTA SDR, COTS UEs, and DDDDDDFUUU TDD"
```

4. Re-parse a saved run if needed:

```bash
python3 -B agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/scripts/p10_multiue_iperf_runner.py \
  --parse-run-dir agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper10_multiue_raw/<run-dir>
```

## Pass Criteria

| Check | Pass Evidence |
|---|---|
| Topology | UE1/UE2/UE3 attach, PDU, TUN, and ping pass. |
| UL fairness | UL receiver Mbps is balanced across active UEs. |
| DL fairness | DL receiver Mbps is balanced across active UEs. |
| Stability | gNB and UE containers remain running after traffic. |

## Limits

- Do not compare absolute Mbps as a final scientific claim.
- RFsim does not reproduce paper RSRP/location axes.
- Paper protocol and traffic details that are not visible in extracted text remain `[Needs Verification]`.
