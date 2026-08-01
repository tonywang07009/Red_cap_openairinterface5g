# Paper-10 Multi-UE Software Throughput 複現教學

[English](./paper10_multiue_software_throughput_tutorial.en.md) | [繁體中文](./paper10_multiue_software_throughput_tutorial.zh-TW.md)

## 目標

- 在 OAI RFsim 複現 Paper-10 multi-UE throughput method。
- 本地範圍：OAI-RAN、OAI CN5G、OAI nrUE containers、3 個 active UEs。
- 分類：[PASS_WITH_GAP] proxy，因為 Paper-10 使用 OTA SDR、Open5GS、COTS devices。

## Inputs

| 項目 | 值 |
|---|---|
| Band | n78-like RFsim profile |
| Bandwidth | 106 PRB at 30 kHz SCS，約 40 MHz |
| UEs | UE1、UE2、UE3 |
| Traffic | iperf3 UDP，180 s |
| 歷史 report | `paper10_multiue_software_throughput_reproduction_2026-05-26_report.md` |

## 流程

1. 啟動 3-UE RFsim topology：

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

2. 確認 readiness：

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

3. 執行 concurrent UL/DL iperf：

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

4. 若需要，重新解析已保存 run：

```bash
python3 -B agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/scripts/p10_multiue_iperf_runner.py \
  --parse-run-dir agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper10_multiue_raw/<run-dir>
```

## 通過標準

| 檢查 | 通過 evidence |
|---|---|
| Topology | UE1/UE2/UE3 attach、PDU、TUN、ping 通過。 |
| UL fairness | UL receiver Mbps 在 active UEs 之間均衡。 |
| DL fairness | DL receiver Mbps 在 active UEs 之間均衡。 |
| Stability | Traffic 後 gNB 與 UE containers 仍在 running。 |

## 限制

- 不把 absolute Mbps 當作最終科學對照結論。
- RFsim 不複現 paper RSRP/location axes。
- Paper protocol 與 traffic details 若 extracted text 看不到，標 `[Needs Verification]`。
