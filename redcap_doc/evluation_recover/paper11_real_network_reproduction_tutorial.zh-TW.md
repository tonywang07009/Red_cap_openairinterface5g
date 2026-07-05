# Paper-11 Service-Gate 複現教學

[English](./paper11_real_network_reproduction_tutorial.en.md) | [繁體中文](./paper11_real_network_reproduction_tutorial.zh-TW.md)

## 目標

- 在 OAI RFsim 複現 Paper-11 service-level RedCap validation logic。
- 量測 UL/DL throughput、UDP loss、jitter、ping RTT。
- 分類：[Service-Gate Proxy]，不是 real-network RF equivalence。

## Inputs

| 項目 | 值 |
|---|---|
| Main script | `redcap_interface/paper11_iperf_live_demo.sh` |
| Display entry | `bash redcap_interface/mmtc.display.bash paper11-live` |
| 歷史筆記 | `paper11_real_network_reproduction_step_by_step.md` |
| Gap diagnosis | `paper11_dl_gap_diagnosis.md` |

## 流程

1. 確認 RFsim runtime 已經啟動：

```bash
docker ps -a
docker exec rfsim5g-oai-nr-ue1_redcap ip -4 -o addr show dev oaitun_ue1
docker exec oai-ext-dn ip -4 -o addr show dev eth0
```

2. 執行可視化 service-gate demo：

```bash
P11_PANEL=1 \
P11_MODE=both \
P11_UL_RATE=17M \
P11_DL_RATE=68M \
P11_DURATION=20 \
bash redcap_interface/paper11_iperf_live_demo.sh
```

3. 視需要執行 application rows：

```bash
# Industrial sensor
P11_PANEL=1 P11_MODE=both P11_UL_RATE=2M P11_DL_RATE=2M P11_DURATION=20 \
  bash redcap_interface/paper11_iperf_live_demo.sh

# Video high-end
P11_PANEL=1 P11_MODE=both P11_UL_RATE=17M P11_DL_RATE=25M P11_DURATION=20 \
  bash redcap_interface/paper11_iperf_live_demo.sh

# Wearable reference
P11_PANEL=1 P11_MODE=both P11_UL_RATE=5M P11_DL_RATE=50M P11_DURATION=20 \
  bash redcap_interface/paper11_iperf_live_demo.sh
```

## 通過標準

| Scenario | Gate |
|---|---|
| Industrial sensor | UL/DL 達到 `2 Mbps`；32-byte RTT 低於 `100 ms`。 |
| Video high-end | DL 達到 `25 Mbps`；RTT 低於 `500 ms`；loss 低於 `1%`。 |
| Wearable | UL 達到 `5 Mbps`；DL 維持在 `5-50 Mbps` reference range。 |
| Far-point service gate | UL 接近 `17 Mbps`；DL `68 Mbps` 可能是 [PASS_WITH_GAP]。 |

## 需要保存的 Evidence

- Ping logs。
- iperf live raw logs。
- `analysis/data/` 底下的 summary CSV。
- `analysis/` 底下的正式 report。

## 限制

- Physical CQT、RSRP/SINR、coverage distance、power-current measurements 都是 proxy-only 或無法直接比較。
- 如果 DL 沒有達標，必須引用 `paper11_dl_gap_diagnosis.md` 說明。
