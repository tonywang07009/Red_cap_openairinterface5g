# RedCap dApp/xApp SDK 開發指南

## Scope

- 本指南提供給要新增或修改 RedCap dApp/xApp SDK algorithm 的工程師。
- 本指南說明目前 SDK contract，不把目前 helper 說成完整 productized O-RAN SDK。
- 所有 runtime claim 仍必須指向 Gate report 與 log。

## Code Locations

| 區域 | 路徑 | 目前角色 |
|---|---|---|
| xApp C SDK | `openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.h` / `.c` | Priority-hint data model 與 selection helper |
| xApp Python helper | `openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.py` | priority-hint logic 的快速 parity helper |
| dApp C SDK | `openair2/E3AP/sdk/redcap_dapp_sdk.h` / `.c` | PRB allocation guard 與 access-pressure policy |
| dApp Python helper | `openair2/E3AP/sdk/redcap_dapp_sdk.py` | dApp policy logic 的快速 parity helper |
| E2/FlexRIC assets | `openair2/E2AP/flexric` | xApp / nearRT-RIC integration route |
| E3 references | `dev_refer/dapp_dev_need/libe3` | dApp-side E3 loopback 與 SWIG reference route |

## Algorithm Contract

- [xApp input]：每個 UE 的 RNTI、UL buffer、QoS weight、RedCap weight 等 metric。
- [xApp output]：以 RedCap priority hint 包裝的 `priority_weight`。
- [dApp input]：RA retry count、Msg3 failure count、PUCCH resource reject count、CRC/discard count、previous pressure EWMA、BWP PRB marker、I/Q availability，以及可選的 xApp priority hint。
- [dApp output]：受限制的 PUCCH/PUSCH ratio intent 與 PRB allocation metadata。
- [Guard boundary]：dApp policy output 必須通過 `redcap_dapp_guard_prb_allocation`，才可視為 applyable。
- [I/Q boundary]：`has_iq_samples` 必須為 true 才能 apply；否則只能維持 reject/diagnostic。

## Current Policy Shape

- [Pressure score]：`50 * ra_retry + 120 * msg3_failure + 160 * pucch_resource_reject + 40 * crc_discard`，上限 clamp 到 `1000`。
- [EWMA]：以整數近似 `0.7 * previous + 0.3 * current`。
- [Low pressure]：PUCCH `200`，PUSCH `600`。
- [Medium pressure]：PUCCH `300`，PUSCH `500`。
- [High pressure]：PUCCH `400`，PUSCH `400`。
- [51 PRB proxy]：Gate E-Core 使用 `MMTC_N_RB_DL=51`；是否可精確稱為 20 MHz 仍標為 `[Needs Verification]`。

## E2 / E3 Boundary

- [E2]：xApp 透過 FlexRIC / nearRT-RIC 進行 RC subscription 與 control-path experiment。
- [Current xApp control proof]：目前有一個 selected RNTI 的 xApp/RIC/gNB ACK/apply 證據。
- [Gate E-Core boundary]：56 UE A/B run 證明 dApp marker 與 access-latency comparison，不證明每個 UE 都受到 xApp 影響。
- [E3]：`dev_refer/dapp_dev_need/libe3` 是 dApp-side RAN-role / DAPP-role communication 的參考路徑。
- [SWIG status]：definition 已存在；generated/importable SWIG runtime module 不是 Gate E-Core 必要 PASS 條件。

## Development Workflow

1. 先更新 Python helper，快速確認 algorithm intent。
2. 在 C SDK 中保持相同欄位語意。
3. 保留 guard boundary；不要繞過 `redcap_dapp_guard_prb_allocation`。
4. 執行 SDK contract self-test：

```bash
python3 agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/dapp_xapp_sdk_contract_selftest.py
```

5. 執行專案 static checker：

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/check_dapp_xapp_sdk_test_validation.py
```

6. 執行 OpenSpec validation：

```bash
openspec validate redcap-dapp-xapp-sdk-test-validation --strict
```

7. Runtime evidence 請依照 [Gate E-Core 手動復現](./gate_e_core56_manual_reproduction.zh-TW.md)。

## Reporting Rules

- 不要把 static checker PASS 寫成 runtime PASS。
- 不要把 KPM 描述成 control path。
- 不要把 Python helper 說成 SWIG runtime binding，除非 generated/importable module 已驗證。
- 不要用已接受的 Gate E-Core run 宣稱 dApp latency improvement；目前只證明有效 A/B comparison。
- 每個 runtime claim 都必須包含 summary metrics、gNB marker evidence，以及 log/report path。
