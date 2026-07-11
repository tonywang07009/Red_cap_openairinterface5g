# Adaptive C-DRX A/B Gate 報告

## Gate 摘要

- [日期]: 2026-07-11。
- [範圍]: 一台處於 `RRC_CONNECTED` 的 RedCap UE，DL 與 UL 分別執行 Arm A/B campaign。
- [整體結果]: runtime A/B 驗證為 **BLOCKED**。
- [Source Readiness]: gNB、UE、本地控制模組與 focused tests 均通過。
- [Runtime 邊界]: 尚無 adaptive-DRX RFsim campaign artifact。每個 campaign 的可證明 scored population 為 `0/300`，總計 `0/1200`。
- [宣告邊界]: 不宣稱 latency、throughput、retransmission、monitoring-time、energy proxy 或實體耗電結果。

## 凍結的 Manifest

已審查並凍結的實驗合約位於：

- `openspec/changes/adaptive-drx-ab-validation/review/experiment_manifest_v1.yaml`
- `openspec/changes/adaptive-drx-ab-validation/review/drx_policy_contract_v1.yaml`

| Campaign | Arm | 方向 | 控制模式 | 規劃 arrivals | Warm-up | 規劃 scored | 已有證據 scored | 狀態 |
|---|---|---|---|---:|---:|---:|---:|---|
| `arm-a-dl` | A | Downlink | 固定 seed 的本地 RRC profile | 330 | 30 | 300 | 0 | BLOCKED / 尚未執行 |
| `arm-b-dl` | B | Downlink | Adaptive E2SM-RC Style 2 / Action 1 | 330 | 30 | 300 | 0 | BLOCKED / 尚未執行 |
| `arm-a-ul` | A | Uplink | 固定 seed 的本地 RRC profile | 330 | 30 | 300 | 0 | BLOCKED / 尚未執行 |
| `arm-b-ul` | B | Uplink | Adaptive E2SM-RC Style 2 / Action 1 | 330 | 30 | 300 | 0 | BLOCKED / 尚未執行 |
| **總計** | | | | **1320** | **120** | **1200** | **0** | **BLOCKED** |

Trace seed 與 Arm A profile seed 仍為 `required_at_run`。目前 worktree 內沒有產生後的 `adaptive_drx_campaign_manifest_v1.json`、trace CSV、command-plan JSONL、metrics CSV 或已關聯的 runtime log。

## Build 與 Test 證據

| Surface | 結果 | 證據 |
|---|---|---|
| 完整 gNB build，包含 gNB scheduler、DRX state、RRC handler 與 C dApp SDK | PASS | `test_log/build_logs/build_nr-softmodem_2026-07-11_00-31-09_adaptive-drx.log` |
| 最終 gNB incremental link | PASS | `test_log/build_logs/build_nr-softmodem_2026-07-11_00-50-00_adaptive-drx.log` |
| UE build，包含 `config_ue.c`、`nr_ue_drx.c`、`nr_ue_procedures.c` 與 `nr_ue_scheduler.c` | PASS | `test_log/build_logs/build_nr-uesoftmodem_2026-07-11_00-53-00_adaptive-drx.log` |
| 本地 CI/telnet DRX 控制模組 | PASS | `test_log/build_logs/build_telnetsrv_ci_2026-07-11_01-03-00_adaptive-drx.log` |
| Focused UE DRX、RC helper 與 gNB DRX CTest targets | PASS，3/3 | `test_log/compiler_logs/ctest_adaptive_drx_final_2026-07-11_01-04-00.log` |
| Deterministic trace、predictor、window 與 checker tests | PASS，4/4 | `test_log/compiler_logs/test_adaptive_drx_python_2026-07-11_00-57-00.log` |
| C dApp guard self-check | PASS | `test_log/compiler_logs/test_redcap_dapp_drx_2026-07-11_00-58-00.log` |
| C xApp RC request-builder self-check | PASS | `test_log/compiler_logs/test_redcap_xapp_drx_2026-07-11_00-59-00.log` |
| SDK static validation | PASS，SWIG module 顯示為 `definition-only` | `test_log/compiler_logs/check_dapp_xapp_sdk_2026-07-11_01-05-00.log` |
| SDK contract self-test | PASS | `test_log/compiler_logs/dapp_xapp_contract_2026-07-11_01-05-00.log` |

這些檢查只證明 source-level 行為與 buildability。Python tests 在暫存目錄建立 synthetic evidence，不能視為 RFsim campaign 結果。

## Runtime Metrics

由於沒有 observed scored rows 或 adaptive-DRX runtime logs，所有凍結的 metrics 均無法取得。

| Metric | Arm A DL | Arm B DL | Arm A UL | Arm B UL | 證據狀態 |
|---|---|---|---|---|---|
| `scored_delivery_success_count` | N/A | N/A | N/A | N/A | Campaign 尚未執行 |
| `scheduled_to_first_receive_latency_ms` | N/A | N/A | N/A | N/A | 現有 metrics CSV 未擷取 receive timestamp |
| `latency_median_ms` | N/A | N/A | N/A | N/A | 沒有 scored latency population |
| `latency_p95_ms` | N/A | N/A | N/A | N/A | 沒有 scored latency population |
| `latency_max_ms` | N/A | N/A | N/A | N/A | 沒有 scored latency population |
| `pdcch_monitoring_slot_ratio` | N/A | N/A | N/A | N/A | 沒有 monitoring-slot counter/export |
| `drx_active_time_slot_ratio` | N/A | N/A | N/A | N/A | 沒有 Active-Time counter/export |
| `burst_goodput_mbps` | N/A | N/A | N/A | N/A | Raw iPerf output 尚未解析至 metrics CSV |
| `udp_loss_percent` | N/A | N/A | N/A | N/A | Raw iPerf output 尚未解析至 metrics CSV |
| `udp_jitter_ms` | N/A | N/A | N/A | N/A | Raw iPerf output 尚未解析至 metrics CSV |
| `dl_harq_retransmission_count` | N/A | N/A | N/A | N/A | 沒有 campaign HARQ counter/export |
| `ul_harq_retransmission_count` | N/A | N/A | N/A | N/A | 沒有 campaign HARQ counter/export |
| `policy_apply_latency_ms` | N/A | N/A | N/A | N/A | 沒有 request-to-completion 關聯時間戳 |
| `policy_reject_count` | N/A | N/A | N/A | N/A | 沒有 runtime decisions |
| `rollback_count` | N/A | N/A | N/A | N/A | 沒有 runtime decisions |
| `rrc_reconfiguration_count` | N/A | N/A | N/A | N/A | 沒有 runtime marker population |
| `rrc_reconfiguration_timeout_count` | N/A | N/A | N/A | N/A | 沒有 runtime marker population |

`N/A` 表示尚未量測，不能解讀為事件數為零或傳送成功。

## Instrumentation 缺口

`scripts/adaptive_drx/run_campaign.py` 目前寫入以下 metrics columns：

```text
campaign_id,arrival_id,scheduled_source_tx_time_us,delivery_success,
policy_version,profile_id,client_launch_time_us,iperf_returncode
```

`scripts/adaptive_drx/check_campaign.py` 可以驗證 300 筆唯一 scored rows、十個 policy versions 且每版 30 筆、trace timestamps、approved profiles、delivery status 與必要 runtime markers。它尚未產生凍結 manifest 要求的 latency、goodput、loss、jitter、HARQ、monitoring-slot 或 Active-Time metrics。Command-plan JSONL 會保留 raw iPerf stdout/stderr，但仍需解析；MAC monitoring 與 HARQ proxies 需要明確的 counter 或 log export。

## E2 與 SWIG 邊界

- Host 的 SWIG 為 `4.0.2`；`openair2/E2AP/flexric/src/xApp/swig/CMakeLists.txt` 要求 SWIG `4.1` 以上。
- `cmake_targets/ran_build/build/CMakeCache.txt` 與 `cmake_targets/ran_build/build_test/CMakeCache.txt` 都記錄 `E2_AGENT=OFF`。
- 因此，通過的 softmodem builds 並未證明主要 `ran_func_rc.c` E2 path 已完成編譯或 runtime execution。
- SDK static check 明確將 generated SWIG module 回報為 `definition-only`；本 Gate 尚未證明 Python `xapp_sdk` import 或 live E2 control request。

## RFsim 與實體耗電邊界

RFsim 不會量測 UE receiver current、watts、joules 或 battery life。完成的 RFsim campaign 最多只能把 `pdcch_monitoring_slot_ratio` 與 `drx_active_time_slot_ratio` 當作 energy-related behavior proxies，並同時呈現 latency、delivery、goodput、loss 與 retransmission 結果。本次證據中連 proxy result 都尚不存在，因此本報告不宣稱節能，也不宣稱實體耗電改善。

## 下一個 Evidence Gate

只有完成並保存下列證據後，runtime Gate 才能從 BLOCKED 改變：

1. 使用 SWIG `>= 4.1` build FlexRIC Python binding，並以 `E2_AGENT=ON` 編譯 gNB。
2. 產生並保存含 seed 的 JSON manifest，以及配對的 DL/UL trace CSV。
3. 補上 frozen metric list 所需的結果 parser 與 MAC/HARQ/monitoring counters。
4. 在 live gNB、UE、E2 connection、常駐 iPerf2 server 與 combined runtime log 環境執行四個 campaigns。
5. 每個 campaign 保存正好 330 個 arrivals，並以 arrivals 31 至 330 形成 300 筆已關聯的 scored rows。
6. 依 policy version 關聯 request、E2 acknowledgement、dApp decision、gNB apply、UE configuration 與 RRC completion markers。
7. 對每個 campaign 執行 `check_campaign.py`，四個結果都必須 PASS，之後才能計算或比較 Arm A/B statistics。

在這些證據完成前，OpenSpec task 2.11 與 adaptive C-DRX runtime Gate 都仍未完成。
