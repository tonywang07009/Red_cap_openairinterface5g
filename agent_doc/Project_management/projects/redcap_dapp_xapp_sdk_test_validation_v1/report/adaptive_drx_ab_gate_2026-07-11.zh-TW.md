# Adaptive C-DRX A/B Gate 報告

## Gate 摘要

- [日期]: 2026-07-11。
- [範圍]: 一台處於 `RRC_CONNECTED` 的 RedCap UE，DL 與 UL 分別執行 Arm A/B campaign。
- [整體結果]: runtime A/B 驗證為 **BLOCKED**。
- [Source Readiness]: E2-enabled gNB/UE、本地 gNB/UE 控制模組、Python xApp import、collectors、checker 與 focused tests 均通過。
- [Runtime Smoke]: 重建 images 已通過單 UE attach/PDU/TUN/ping、E2 Setup、固定 Arm A apply/RRC completion、UE Active-Time export，以及雙向各一個 fixed-byte burst。
- [Runtime 邊界]: 尚無完整 adaptive-DRX campaign artifact。每個 campaign 的可證明 scored population 為 `0/300`，總計 `0/1200`。
- [宣告邊界]: Smoke values 只作 connectivity/control evidence；不宣稱 A/B latency、throughput、retransmission、monitoring-time、energy proxy 或實體耗電結果。

## 凍結的 Manifest

已審查並凍結的實驗合約位於：

- `openspec/changes/adaptive-drx-ab-validation/review/experiment_manifest_v1.yaml`
- `openspec/changes/adaptive-drx-ab-validation/review/drx_policy_contract_v1.yaml`

| Campaign | Arm | 方向 | 控制模式 | 規劃 arrivals | Warm-up | 規劃 scored | 已有證據 scored | 狀態 |
|---|---|---|---|---:|---:|---:|---:|---|
| `arm-a-dl` | A | Downlink | 固定 `drx-320-10`，只套用一次 | 330 | 30 | 300 | 0 | BLOCKED / 尚未執行 |
| `arm-b-dl` | B | Downlink | Adaptive E2SM-RC Style 2 / Action 1 | 330 | 30 | 300 | 0 | BLOCKED / 尚未執行 |
| `arm-a-ul` | A | Uplink | 固定 `drx-320-10`，只套用一次 | 330 | 30 | 300 | 0 | BLOCKED / 尚未執行 |
| `arm-b-ul` | B | Uplink | Adaptive E2SM-RC Style 2 / Action 1 | 330 | 30 | 300 | 0 | BLOCKED / 尚未執行 |
| **總計** | | | | **1320** | **120** | **1200** | **0** | **BLOCKED** |

Trace seed 仍為 `required_at_run`；Arm A 沒有 profile seed。四個 campaigns 的 generated runtime artifacts 尚未收集。

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
| E2-enabled gNB/UE 與 `telnetsrv_ci`/`ciUE` build | PASS | `test_log/build_logs/build_e2_agent_telnet_gnb_ue_2026-07-11_16-02-bootstrap-metrics.log` |
| FlexRIC SWIG 4.1.1 Python bridge build/import | PASS | `test_log/build_logs/build_xapp_sdk_2026-07-11_15-13-45_swig411.log`；`test_log/compiler_logs/xapp_sdk_import_2026-07-11_15-13-45_swig411.log` |
| Adaptive 與 evidence Python tests | PASS，10/10 與 3/3 | 本次 focused test run |
| 本次 focused C-DRX rebuild/CTest | PASS，gNB 8/8、UE 9/9、RC 3/3 | `test_log/compiler_logs/adaptive_drx_focused_ctest_2026-07-11_20-05-02.log`；同 timestamp detailed suite logs |
| E2-enabled RFsim image rebuild | PASS | `test_log/build_logs/rebuild_local_oai_images_2026-07-11_20-05-02_adaptive-drx.log` |
| UE image receiver-capture dependency | PASS，已加入 `tcpdump` | `test_log/build_logs/rebuild_oai_nr_ue_tcpdump_2026-07-11_20-05-02.log` |

這些檢查只證明 source-level 行為與 buildability。Python tests 在暫存目錄建立 synthetic evidence，不能視為 RFsim campaign 結果。

## Runtime Smoke 證據

| 檢查 | 結果 | 證據 |
|---|---|---|
| UE1 attach/PDU/TUN/ping；gNB restart | PASS `1/1/1/1`；restart `0` | `test_log/compiler_logs/adaptive_drx_rfsim_prereq_2026-07-11_20-05-02.log` |
| E2 Setup request/response | PASS | `test_log/compiler_logs/mmtc_smoke_2026-07-11_20-14-07_gnb.log` |
| Arm A `drx-320-10` policy version 1 | PASS staged/applied/RRC complete | `test_log/compiler_logs/adaptive_drx_live_arm_a_apply_2026-07-11_20-05-02.log` |
| UE Active-Time export | PASS；live counter 符合 `active_slots <= observed_slots` | `ciUE drx_stats` runtime query |
| 綁定 `10.0.0.2` 的 fixed-byte UL burst | PASS；receiver report，loss `0/29` | `test_log/compiler_logs/adaptive_drx_live_ul_burst_2026-07-11_20-05-02_bind-fix.log` |
| 綁定 `10.0.0.2` 的 fixed-byte DL reverse burst | PASS；receiver report，loss `1/29` | `test_log/compiler_logs/adaptive_drx_live_dl_burst_2026-07-11_20-05-02_bind-fix.log` |

Smoke 發現並修正 route-integrity 問題：runtime execution 現在強制要求 `--bind-address`，並映射為 iPerf2 `-B`，避免 traffic 由 container `eth0` 繞過 UE PDU-session route。

## Runtime Metrics

由於沒有 observed scored rows 或 adaptive-DRX runtime logs，所有凍結的 metrics 均無法取得。

| Metric | Arm A DL | Arm B DL | Arm A UL | Arm B UL | 證據狀態 |
|---|---|---|---|---|---|
| `scored_delivery_success_count` | N/A | N/A | N/A | N/A | Campaign 尚未執行 |
| `scheduled_to_first_receive_latency_ms` | N/A | N/A | N/A | N/A | Collector/checker ready；尚無 campaign capture |
| `latency_median_ms` | N/A | N/A | N/A | N/A | 沒有 scored latency population |
| `latency_p95_ms` | N/A | N/A | N/A | N/A | 沒有 scored latency population |
| `latency_max_ms` | N/A | N/A | N/A | N/A | 沒有 scored latency population |
| `pdcch_monitoring_slot_ratio` | N/A | N/A | N/A | N/A | UE counter/export ready；尚無 campaign summary |
| `drx_active_time_slot_ratio` | N/A | N/A | N/A | N/A | UE counter/export ready；尚無 campaign summary |
| `burst_goodput_mbps` | N/A | N/A | N/A | N/A | Parser ready；尚無 campaign iPerf output |
| `udp_loss_percent` | N/A | N/A | N/A | N/A | Parser ready；尚無 campaign iPerf output |
| `udp_jitter_ms` | N/A | N/A | N/A | N/A | Parser ready；尚無 campaign iPerf output |
| `dl_harq_retransmission_count` | N/A | N/A | N/A | N/A | Log-delta parser ready；尚無 campaign snapshots |
| `ul_harq_retransmission_count` | N/A | N/A | N/A | N/A | Log-delta parser ready；尚無 campaign snapshots |
| `policy_apply_latency_ms` | N/A | N/A | N/A | N/A | Timestamp correlation ready；尚無 runtime markers |
| `policy_reject_count` | N/A | N/A | N/A | N/A | 沒有 runtime decisions |
| `rollback_count` | N/A | N/A | N/A | N/A | 沒有 runtime decisions |
| `rrc_reconfiguration_count` | N/A | N/A | N/A | N/A | 沒有 runtime marker population |
| `rrc_reconfiguration_timeout_count` | N/A | N/A | N/A | N/A | 沒有 runtime marker population |

`N/A` 表示尚未量測，不能解讀為事件數為零或傳送成功。

## Instrumentation Readiness

`scripts/adaptive_drx/run_campaign.py` 目前寫入以下 metrics columns：

```text
campaign_id,arrival_id,scheduled_source_tx_time_us,delivery_success,
policy_version,profile_id,client_launch_time_us,iperf_returncode,
burst_goodput_mbps,udp_jitter_ms,udp_lost_packets,udp_total_packets,udp_loss_percent
```

`check_campaign.py` 可驗證 traffic metrics、receiver CSV、UE Active-Time summary、staged-to-RRC latency、RNTI-specific HARQ delta、versions、profiles 與 markers。`adaptive_drx.py receive-csv` 可轉換 filtered tcpdump log。這是 source readiness，不是已量測 RFsim evidence。

## E2 與 SWIG 邊界

- 系統 SWIG 是 4.0.2；repository SWIG 4.1.1 已成功為 Python 3.12 build/import `xapp_sdk`。
- 隔離的 `/tmp/oai-e2-agent-build` 記錄 `E2_AGENT=ON`；兩個 softmodems 與兩個 telnet modules 都可 build。
- gNB 已與 running Near-RT RIC 完成 E2 Setup。Live Arm B Python request 尚未驗證，因 workspace elevation credits 用盡後，受控 host-to-Docker bridge access 被拒絕。

## RFsim 與實體耗電邊界

RFsim 不會量測 UE receiver current、watts、joules 或 battery life。完成的 RFsim campaign 最多只能把 `pdcch_monitoring_slot_ratio` 與 `drx_active_time_slot_ratio` 當作 energy-related behavior proxies，並同時呈現 latency、delivery、goodput、loss 與 retransmission 結果。Smoke counter 不是 scored A/B proxy population，因此本報告不宣稱節能，也不宣稱實體耗電改善。

## 教育測試筆記

### 1. Technical Background

C-DRX 限制 `RRC_CONNECTED` UE 必須監聽 PDCCH 的時段。Network 配置合法 timer/cycle values，UE MAC 根據 timers 與 runtime events 執行 Active Time。gNB scheduler 必須使用相同 profile，避免在 UE 不處於 Active Time 時排程一般 new data。本實驗比較固定 profile 與每 30 arrivals 更新的 adaptive policy；RFsim counters 只能作 behavior proxies，不是耗電量測。

### 2. Key C Functions / Data Structures

- `nr_mac_apply_drx_policy()`、`nr_gnb_drx_state_t`：gNB staged policy、apply、rollback 與 version state。
- `nr_ue_drx_is_active()`、`nr_ue_drx_slot_counts_t`：UE Active-Time decision 與 atomic counters。
- `redcap_dapp_guard_e2_drx_cycle()`：live E2 cycle request 的 narrow legal/state guard。

### 3. Test Results Summary

| Test Item | Pass-Fail | Code Coverage | Modification Logs |
|---|---|---|---|
| gNB C-DRX state/guard | PASS 8/8 | N/A，未啟用 coverage | `test_nr_gnb_drx_2026-07-11_20-05-02.log` |
| UE C-DRX Active Time | PASS 9/9 | N/A，未啟用 coverage | `test_nr_ue_drx_2026-07-11_20-05-02.log` |
| RC request contract | PASS 3/3 | N/A，未啟用 coverage | `test_nr_redcap_rc_ctrl_2026-07-11_20-05-02.log` |
| 單 UE RFsim smoke | PASS；A/B Gate 仍 BLOCKED | N/A，runtime proxy | `adaptive_drx_rfsim_prereq_2026-07-11_20-05-02.log` |

### 4. 3GPP Specification Mapping

- [TS 38.321 §5.7]：MAC DRX operation 依 On Duration、inactivity、HARQ、SR 與相關 events 決定 Active Time。
- [TS 38.331 §6.3.2]：`DRX-Config` 承載 RRC 配置的 timer、cycle 與 offset fields；release-specific ASN.1 field applicability 仍需依 frozen local release text 標記 `[Needs Verification]`。

### 5. Practice Exercises

1. [Basic]：說明為何 On Duration 控制 UE PDCCH monitoring，而不是 gNB sleep。
2. [Applied]：從 telnet request trace policy version 1 到 RRC-complete marker。
3. [Advanced]：設計 failure test，證明 rejected Arm B window 會保留且 rollback state 不變。

## 下一個 Evidence Gate

只有完成並保存下列證據後，runtime Gate 才能從 BLOCKED 改變：

1. 恢復受控 host-to-Docker bridge access，並證明 Python `xapp_sdk` node discovery。
2. 產生/rebase future JSON manifest，使用 `--bind-address` 執行四個 campaigns。
3. 每個 campaign 保存正好 330 個 arrivals，並以 arrivals 31 至 330 形成 300 筆已關聯的 scored rows。
4. 依 policy version 關聯 request、E2 acknowledgement、dApp decision、gNB apply、UE configuration 與 RRC completion markers。
5. 對每個 campaign 執行 `check_campaign.py`，四個結果都必須 PASS，之後才能計算或比較 Arm A/B statistics。

OpenSpec task 2.11 已完成 source implementation。Task 2.12 與 adaptive C-DRX runtime Gate 要等上述證據完成。
