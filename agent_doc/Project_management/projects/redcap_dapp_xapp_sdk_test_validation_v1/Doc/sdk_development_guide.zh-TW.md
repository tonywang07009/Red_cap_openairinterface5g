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
| dApp C SDK | `openair2/E3AP/sdk/redcap_dapp_sdk.h` / `.c` | PRB allocation guard、access-pressure policy 與 RA-pressure selector |
| dApp Python helper | `openair2/E3AP/sdk/redcap_dapp_sdk.py` | dApp policy / selector logic 的快速 parity helper |
| E2/FlexRIC assets | `openair2/E2AP/flexric` | xApp / nearRT-RIC integration route |
| E3 references | `Apps_dev/dapp_dev_need/libe3` | dApp-side E3 loopback 與 SWIG reference route |

## 參考：證據標籤

- `Public`：已在 C header 宣告或由 Python module 支援。
- `Integrated`：正式控制路徑已有 caller 與可辨識的套用邊界。
- `Runtime-evidenced`：保留證據含對應 runtime marker。
- `Dormant/blocked`：已實作，但缺少正式 caller、套用路徑或 runtime proof。

以下卡片以 repository source 與本機保留證據為準。沒有本機條文依據的 O-RAN 或 3GPP 對應維持 `[Needs Verification]`。

## 參考：xApp API 卡片

### `redcap_xapp_make_ul_prb_ctrl_req`

- **問題／時機**：選好 live UE 並驗證 cap 後，建立 E2SM-RC UL PRB-cap request。
- **C／Python**：`rc_ctrl_req_data_t redcap_xapp_make_ul_prb_ctrl_req(uint64_t ue_id, uint16_t rnti, uint16_t max_ul_prb)`／`make_ul_prb_ctrl_request(ue_id: int, rnti: int, max_ul_prb: int) -> RedCapUlPrbCtrlRequest`。
- **輸入／輸出／狀態**：caller 持有 UE ID、RNTI、cap、request 與 C allocation。C builder 不拒絕 0 或超界值，邊界由 caller/downstream guard 負責；Python 會檢查 dataclass input。
- **Trace**：caller 為 `ci-scripts/redcap_ul_prb_ctrl_xapp.c`；callee 建立 UE ID 與 integer RAN parameters；下游套用點是 `ran_func_rc.c` 的 `apply_redcap_ul_prb_control`。
- **Marker／下一步／證據**：從 `CONTROL ACK rx` 追到 gNB `RedCap UL PRB control ... effective ...`；證據為 `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-09_00-00-46*.log`。狀態：`Public`、`Integrated`、`Runtime-evidenced`。

### `redcap_xapp_make_drx_ctrl_req`

- **問題／時機**：選定 UE 與 policy 後，為核准 cycle 建立 DRX E2SM-RC request。
- **C／Python**：`bool redcap_xapp_make_drx_ctrl_req(uint64_t ue_id, uint16_t long_cycle_ms, rc_ctrl_req_data_t *ctrl_req)`／`make_drx_ctrl_request(ue_id: int, long_cycle_ms: int, ric_request_id: int, policy_version: int) -> RedCapDrxCtrlRequest`。
- **輸入／輸出／狀態**：核准 cycle 為 `320, 640, 1280, 2560, 5120, 10240` ms。caller 持有結果與 C allocation。C 拒絕 UE 0、null output、不支援 cycle 與 allocation failure；Python 另有 C signature 沒有的 correlation 欄位。
- **Trace**：已證明 C caller 是 `test_redcap_xapp_drx.c`；callee 建立 UE ID 與 integer parameter。Live adaptive runner 使用另一條 Python/SWIG control path，因此此 helper 的 production caller/apply point 為 `[Needs Verification]`。
- **Marker／下一步／證據**：builder 不輸出 marker。Live DRX 從 `ran_func_rc.c` 追到 `redcap_dapp_guard_e2_drx_cycle`。狀態：`Public`、`Dormant/blocked`；沒有此 helper 的獨立 runtime evidence。

### `redcap_xapp_find_rc_ran_func_idx`

- **問題／時機**：subscription 或 control 前，在 connected E2 node 找 RC RAN function。
- **C／Python**：`ssize_t redcap_xapp_find_rc_ran_func_idx(const e2_node_connected_xapp_t *node)`／`find_rc_ran_func_idx(ran_functions: Sequence[Mapping[str, Any]]) -> int`。
- **輸入／輸出／狀態**：caller 持有 node/function list；回傳 index 或 `-1`。C 拒絕 null 並掃描 `len_rf`；不修改 shared state。
- **Trace**：caller 是 `ci-scripts/redcap_ul_prb_ctrl_xapp.c`；比對 `SM_RC_ID` 或 `RC_RAN_FUNC_DEF_E`；index 用來選 RC path。
- **Marker／下一步／證據**：沒有專用 marker；接著追 caller 的 subscription/control setup。已成功保留的 RC control 間接證明此 lookup path。狀態：`Public`、`Integrated`、間接 `Runtime-evidenced`。

### `redcap_xapp_make_priority_hint`

- **問題／時機**：選取或轉送候選 UE 前，把單一 metric 轉成 bounded priority hint。
- **C／Python**：`bool redcap_xapp_make_priority_hint(const redcap_xapp_ue_metric_t *metric, uint16_t validity_ms, redcap_xapp_priority_hint_t *hint)`／`make_priority_hint(metric: RedCapUeMetric, validity_ms: int) -> RedCapPriorityHint`。
- **輸入／輸出／狀態**：caller 持有 metric/result；權重為 `UL bytes / 1024 + QoS + RedCap` 並飽和到 `uint16`。C 拒絕 null、RNTI 0、validity 0；Python 另外拒絕負數與超過欄位上限的值。
- **Trace**：C caller 是 `redcap_xapp_select_top_priority_hint`；Python caller 是 selection 與 self-check。尚未證明正式 control conversion caller。
- **Marker／下一步／證據**：result 含 `RedCap xApp priority hint`，但沒有正式路徑保留 log。下一步找非測試 caller 與 RC-request conversion。狀態：`Public`、`Dormant/blocked`。

### `redcap_xapp_select_top_priority_hint`

- **問題／時機**：選最高權重 UE；同分時選較小 RNTI。
- **C／Python**：`bool redcap_xapp_select_top_priority_hint(const redcap_xapp_ue_metric_t *metrics, size_t metrics_len, uint16_t validity_ms, redcap_xapp_priority_hint_t *hint)`／`select_top_priority_hint(metrics: Sequence[RedCapUeMetric], validity_ms: int) -> RedCapPriorityHint`。
- **輸入／輸出／狀態**：caller 持有 list/result；無 shared state。C 拒絕 null/empty 並跳過無效候選；Python 對 empty 或第一個無效 metric 拋例外，兩者的無效元素行為不完全一致。
- **Trace**：呼叫 single-hint builder。已證明 caller 只有 static check 與 Python self-test；production caller/apply point 為 `[Needs Verification]`。
- **Marker／下一步／證據**：結果含 `RedCap xApp priority hint`，沒有對應 production log。狀態：`Public`、`Dormant/blocked`。

## 參考：dApp API 卡片

### `redcap_dapp_guard_ul_prb_cap` 與 `redcap_dapp_guard_allows_apply`

- **問題／時機**：只有 RNTI 與 contract range 有效時才接受 requested UL cap。
- **C／Python**：`redcap_dapp_guard_result_t redcap_dapp_guard_ul_prb_cap(const redcap_dapp_ul_prb_request_t *request)` 加上 `bool redcap_dapp_guard_allows_apply(...)`；Python 使用同名函式與對應 dataclass。
- **輸入／輸出／狀態**：caller 持有 request/result；拒絕 null、RNTI 0、min/max 顛倒或 cap 超出 inclusive range；無 shared state。
- **Trace**：目前 caller 是 Python self-check；未證明 production caller 或 scheduler apply point。
- **Marker／下一步／證據**：沒有 runtime marker。宣稱 enforcement 前先找到 production caller。狀態：`Public`、`Dormant/blocked`。

### `redcap_dapp_guard_prb_allocation` 與 `redcap_dapp_prb_allocation_allows_apply`

- **問題／時機**：驗證 BWP/IQ/ratio intent，並把通過的 permille 換算成 PRB 數。
- **C／Python**：`redcap_dapp_prb_allocation_result_t redcap_dapp_guard_prb_allocation(const redcap_dapp_prb_allocation_request_t *request)` 與 `allows_apply` helper；Python 使用對應同名函式與 dataclass。
- **輸入／輸出／狀態**：caller 持有資料；接受 BWP `11`、`12`、`51`，要求非零 RNTI 與 IQ evidence，拒絕任一 ratio 或合計超過 `1000`。輸出採向上取整；無 shared state。
- **Trace**：production caller 是 `gNB_scheduler_uci.c` PUCCH hook 與 `gNB_scheduler_ulsch.c` UL hook；內部 callee 做 ratio 換算。目前 hook 在 scheduler 欄位建立後觀測/記錄，allocation mutation 為 `[Needs Verification]`。
- **Marker／下一步／證據**：`RedCap dApp PRB decision`；Gate D 證據為 `test_log/runtime_logs/gate_d_access_pressure_gnb_2026-07-07_00-47_local_no_csirs_srs.log`。狀態：`Public`、`Integrated`、`Runtime-evidenced`；enforcement 尚未證明。

### `redcap_dapp_access_pressure_policy` 與 `redcap_dapp_access_pressure_allows_apply`

- **問題／時機**：把 access counters 與 prior EWMA 轉成 low/medium/high ratio intent，再做 allocation guard。
- **C／Python**：`redcap_dapp_access_pressure_result_t redcap_dapp_access_pressure_policy(const redcap_dapp_access_pressure_request_t *request)` 加上 `allows_apply` helper；Python 對應同名函式。
- **輸入／輸出／狀態**：caller 持有 counter/state/result。Policy 把 pressure clamp 到 `1000`，計算 integer EWMA、選固定 ratios，再呼叫 `redcap_dapp_guard_prb_allocation`；RNTI/BWP/IQ rejection 由 guard 負責。
- **Trace**：caller 是 RA selector 與 self-test。gNB production path 沒有套用 policy result；目前 PUCCH/UL hook 直接呼叫較低層的 allocation guard。
- **Marker／下一步／證據**：result 含 `RedCap dApp access pressure policy`，沒有正式 apply marker。狀態：`Public`；production application 為 `Dormant/blocked`。

### `redcap_dapp_select_ra_pressure_priority`

- **問題／時機**：先依 RA retry，再依 pressure、priority 與較小 RNTI 選 UE。
- **C／Python**：`redcap_dapp_access_pressure_selection_t redcap_dapp_select_ra_pressure_priority(const redcap_dapp_access_pressure_request_t *requests, size_t request_count)`／對應 Python 函式回傳 `RedCapDappAccessPressureSelection`。
- **輸入／輸出／狀態**：caller 持有 list/result；null/empty 或全為 RNTI 0 時回傳 `found=false`。對選中 UE 呼叫 `redcap_dapp_access_pressure_policy`；無 shared state。
- **Trace**：Python 實驗 caller 是 `select_core36_pressure_priority.py`；C caller 只有 self-check/static。實驗會寫入 `MMTC_DAPP_PRIORITY_UES`；C production scheduler apply point 為 `[Needs Verification]`。
- **Marker／下一步／證據**：result 含 `RedCap dApp RA pressure priority`；Core36 report 證明實驗 selection，不證明 mitigation improvement。狀態：`Public`；Python experiment-integrated；C path 為 `Dormant/blocked`。

### `redcap_dapp_guard_drx_policy` 與 `redcap_dapp_drx_guard_allows_apply`

- **問題／時機**：驗證 prediction-derived DRX profile、policy version、cooldown 與 rollback state。
- **C／Python**：只有 C：`redcap_dapp_drx_guard_result_t redcap_dapp_guard_drx_policy(const redcap_dapp_drx_policy_request_t *request, const redcap_dapp_drx_config_t *current)` 加上 `redcap_dapp_drx_guard_allows_apply`；沒有 Python mirror。
- **輸入／輸出／狀態**：caller 持有 request/current/result；拒絕 schema、RNTI、連線、stale version、sample count、prediction bounds、cycle、cooldown 與 rollback failure。ACK 保留 previous state；無 shared state。
- **Trace**：caller 是 focused C tests。Live E2 control 使用下一張卡片的 narrow E2-cycle guard，不使用本 prediction guard。
- **Marker／下一步／證據**：`[RedCap DRX][dApp ACCEPT]` 或 `REJECT`；沒有把 retained runtime proof 歸給此 exact function。狀態：`Public`、`Dormant/blocked`。

### `redcap_dapp_guard_e2_drx_cycle`

- **問題／時機**：套用到 gNB MAC/RRC state 前，防護 live E2 DRX-cycle request。
- **C／Python**：只有 C：`redcap_dapp_drx_guard_result_t redcap_dapp_guard_e2_drx_cycle(const redcap_dapp_e2_drx_cycle_request_t *request, const redcap_dapp_drx_config_t *current)`；沒有 Python mirror。
- **輸入／輸出／狀態**：caller 先 snapshot gNB current state，再持有 request/result。拒絕未知或未連線 UE、stale policy、不支援 cycle、cooldown 未結束與 rollback config 無效。
- **Trace**：production caller 是 `ran_func_rc.c`；ACK 後由 `redcap_dapp_drx_guard_allows_apply` gate `nr_mac_apply_drx_policy`，再進入 RRC reconfiguration。
- **Marker／下一步／證據**：`[RedCap DRX][dApp ACCEPT]`／`REJECT`，再關聯 gNB apply 與 RRC-complete。四個 adaptive DRX campaigns 的證據位於 `test_log/runtime_logs/adaptive_drx_2026-07-13_full_ab/`。狀態：`Public`、`Integrated`、`Runtime-evidenced`。

## 指南：Algorithm Contract

- [xApp input]：每個 UE 的 RNTI、UL buffer、QoS weight、RedCap weight 等 metric。
- [xApp output]：以 RedCap priority hint 包裝的 `priority_weight`。
- [dApp input]：RA retry count、Msg3 failure count、PUCCH resource reject count、CRC/discard count、previous pressure EWMA、BWP PRB marker、I/Q availability，以及可選的 xApp priority hint。
- [dApp output]：受限制的 PUCCH/PUSCH ratio intent、RA-pressure priority selection 與 PRB allocation metadata。
- [Guard boundary]：dApp policy output 必須通過 `redcap_dapp_guard_prb_allocation`，才可視為 applyable。
- [I/Q boundary]：`has_iq_samples` 必須為 true 才能 apply；否則只能維持 reject/diagnostic。

## Current Policy Shape

- [Pressure score]：`100 * ra_retry + 120 * msg3_failure + 160 * pucch_resource_reject + 40 * crc_discard`，上限 clamp 到 `1000`。
- [Priority selector]：`redcap_dapp_select_ra_pressure_priority` 先選 [RA retry count] 最高 UE，再用 pressure score、priority weight、較小 RNTI 做 tie-break。
- [EWMA]：以整數近似 `0.7 * previous + 0.3 * current`。
- [Low pressure]：PUCCH `200`，PUSCH `600`。
- [Medium pressure]：PUCCH `300`，PUSCH `500`。
- [High pressure]：PUCCH `400`，PUSCH `400`。
- [51 PRB proxy]：Gate E-Core 使用 `MMTC_N_RB_DL=51`；是否可精確稱為 20 MHz 仍標為 `[Needs Verification]`。

## E2 / E3 Boundary

- [E2]：xApp 透過 FlexRIC / nearRT-RIC 進行 RC subscription 與 control-path experiment。
- [Current xApp control proof]：目前有一個 selected RNTI 的 xApp/RIC/gNB ACK/apply 證據。
- [Gate E-Core boundary]：56 UE A/B run 證明 dApp marker 與 access-latency comparison，不證明每個 UE 都受到 xApp 影響。
- [E3]：`Apps_dev/dapp_dev_need/libe3` 是 dApp-side RAN-role / DAPP-role communication 的參考路徑。
- [SWIG status]：definition 已存在；generated/importable SWIG runtime module 不是 Gate E-Core 必要 PASS 條件。

## 指南：Development Workflow

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

7. 36 UE pressure evidence 先跑 baseline，再用 `select_core36_pressure_priority.py` 產生 `MMTC_DAPP_PRIORITY_UES`，最後用 `gate_e_64ue_stage_check.py --stage core36-pressure` 驗證。
8. 56 UE runtime evidence 請依照 [Gate E-Core 手動復現](./gate_e_core56_manual_reproduction.zh-TW.md)。

## Reporting Rules

- 不要把 static checker PASS 寫成 runtime PASS。
- 不要把 KPM 描述成 control path。
- 不要把 Python helper 說成 SWIG runtime binding，除非 generated/importable module 已驗證。
- 不要用已接受的 Gate E-Core run 宣稱 dApp latency improvement；目前只證明有效 A/B comparison。
- 每個 runtime claim 都必須包含 summary metrics、gNB marker evidence，以及 log/report path。

## 範例

- [入門建置與 29 UE 重現](../../../../../redcap_doc/manuals/install/redcap_begin_from_zero.zh-TW.md)
- [56 UE 實驗設定檔與 dApp/xApp 重現](./gate_e_core56_manual_reproduction.zh-TW.md)
- [Adaptive C-DRX A/B 手動重現](./adaptive_drx_ab_manual_reproduction.zh-TW.md)
- [正式 RedCap L1-L3 函式索引](../../../../../redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md)
