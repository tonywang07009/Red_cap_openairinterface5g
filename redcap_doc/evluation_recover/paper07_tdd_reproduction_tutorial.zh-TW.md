# Paper-07 TDD Peak-Rate 複現教學

[English](./paper07_tdd_reproduction_tutorial.en.md) | [繁體中文](./paper07_tdd_reproduction_tutorial.zh-TW.md)

## 目標

- 在本地 OAI RFsim path 複現 Paper-07 TDD RedCap peak-rate target。
- Target-rate points：UL `34 Mbps`、DL `140 Mbps`。
- 本地 offered rates：UL `35M`、DL `141M`。
- 分類：[Target-Rate Proxy]，不是一比一 RF/channel 複現。

## Inputs

| 項目 | 值 |
|---|---|
| Scenario | OAI RFsim RedCap TDD n78 |
| Carrier option | 51PRB full-carrier profile，較接近 Paper-07 語意 |
| UL evidence | iperf receiver Mbps 加 MAC `Qm 8` / MCS evidence |
| DL evidence | reverse iperf receiver Mbps 加 DLSCH MCS table evidence |
| 歷史筆記 | `paper07_tdd_reproduction_step_by_step.md` |

## 流程

1. 先完成 `redcap_doc/manuals/install/redcap_begin_from_zero.zh-TW.md`。
2. 開啟 display menu：

```bash
bash redcap_interface/mmtc.display.bash paper07-menu
```

3. 在 legacy Paper-07 menu 選擇：
   - `8) Enable PAPER-07 256QAM profile`
   - `14) Select 51PRB full-carrier profile`
   - `16) Run PAPER-07 reproduction bundle`

4. 若手動執行，使用：
   - UL rate `35M`
   - DL rate `141M`
   - duration `60s`
   - `PUSCH256QAM=1`
   - `PDSCH256QAM=1`

## 通過標準

| 檢查 | 通過 evidence |
|---|---|
| Attach health | UE running、attach、PDU、TUN、forward ping 存在。 |
| UL target | Receiver throughput 達到 Paper-07 UL target-rate window。 |
| DL target | Receiver throughput 達到 Paper-07 DL target-rate window。 |
| MAC evidence | UL/DL MAC logs 顯示預期 QAM/MCS path。 |
| Stability | gNB restart count 維持 `0`。 |

## 需要保存的 Evidence

- Stage 或 smoke summary log。
- iperf UL/DL logs。
- gNB MAC evidence。
- 若有改 capability flags，保存 UE runtime YAML。
- 最終 report 放在 `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/`。

## 已知限制

- RFsim 無法一比一複現 Paper-07 field RF conditions。
- 如果 active bandwidth、BWP 或 carrier semantics 與 paper 不同，結果標為 [PASS_WITH_GAP]。
- 沒有查過本地 3GPP notes 的 exact standard-clause mapping 一律標 `[Needs Verification]`。
