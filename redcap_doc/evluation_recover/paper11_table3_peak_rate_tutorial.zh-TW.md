# Paper-11 Table 3 Peak-Rate 複現教學

[English](./paper11_table3_peak_rate_tutorial.en.md) | [繁體中文](./paper11_table3_peak_rate_tutorial.zh-TW.md)

## 目標

- 在本地 RedCap RFsim path 複現 Paper-11 Table 3 target-rate rows。
- Targets：UL 64QAM `90 Mbps`、DL 64QAM `169.5 Mbps`、DL 256QAM `226 Mbps`。
- 分類：[Target-Rate Proxy]，不是 calibrated 2.1G FDD RF reproduction。

## Inputs

| 項目 | 值 |
|---|---|
| Script | `redcap_interface/paper11_table3_peak_reproduction.sh` |
| Display entry | `bash redcap_interface/mmtc.display.bash paper11-table3` |
| RFsim profile | `P11T3_PROFILE=51prb` |
| 歷史 evidence | `paper11_table3_2p1g_peak_rate_step_by_step.md` |

## 流程

執行 default 51PRB proxy：

```bash
P11T3_PROFILE=51prb P11T3_DURATION=60 bash redcap_interface/paper11_table3_peak_reproduction.sh
```

或使用 display wrapper：

```bash
P11T3_PROFILE=51prb P11T3_DURATION=60 bash redcap_interface/mmtc.display.bash paper11-table3
```

Script 應該會：

1. 啟動 64QAM setup。
2. 執行 UL `90M`。
3. 執行 DL `169.5M`。
4. 重新啟動或套用 DL 256QAM setup。
5. 執行 DL `226M`。
6. 保存 iperf、MAC、runtime YAML evidence。

## 通過標準

| 測試 | 通過 evidence |
|---|---|
| UL 64QAM | Receiver Mbps 達到 `90 Mbps` target-rate window，且 MAC 顯示 64QAM evidence。 |
| DL 64QAM | Receiver Mbps 達到 `169.5 Mbps`，且 DLSCH evidence 穩定。 |
| DL 256QAM | Receiver Mbps 達到 `226 Mbps`，且 MAC 顯示 256QAM table path。 |
| Stability | gNB restart count 維持 `0`。 |

## 限制

- 本地 RFsim 使用 band 78 TDD，不是 paper 的 2.1G FDD condition。
- 這個 run 證明 local simulator path 的 target-rate capacity，不證明 real 2.1G RF equivalence。
- 未來若有穩定 2.1G/FDD RedCap YAML，必須用同一份教學重跑，才能主張 full paper equivalence。
