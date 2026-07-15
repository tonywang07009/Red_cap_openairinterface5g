# 56 UE 實驗設定檔與 dApp/xApp 重現

[English](./gate_e_core56_manual_reproduction.en.md) | [繁體中文](./gate_e_core56_manual_reproduction.zh-TW.md)

## Scope

- 本頁用來手動復現 RedCap dApp/xApp SDK [Gate E-Core] 結果。
- Gate 內容是 56 UE [Baseline] 與 [dApp Enabled] 的接入延遲 A/B 比較。
- 主要指標是 [Launch-to-TUN]：每台 UE launch epoch 到第一次觀察到 `oaitun_ue1`。
- 本頁是手動復現文件；最後接受結果彙整於 `report/gate_e_core56_ab_latency_2026-07-09.md`。
- 執行本實驗前，先完成 [29 UE 入門教學](../../../../../redcap_doc/manuals/install/redcap_begin_from_zero.zh-TW.md)。

## 前置需求

從 repository root 執行：

```bash
test -f oai-cn5g/docker-compose.yaml
test -f ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml
bash redcap_interface/validate_redcap_interface.sh
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_e_64ue_stage_check.py
```

任一指令失敗就不要啟動 RFsim。本教學重用既有 images；若 C 或 SDK integration code 已變更，先重建 images。

## Runtime Profile

- [Repository root]：請從 `/home/tonywang/OAI/Red_cap_openairinterface5g` 執行指令。
- [CN5G source]：wrapper 預設使用 repo 管理的 `oai-cn5g/docker-compose.yaml`。
- [RFsim source]：`ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`。
- [gNB profile]：`ci-scripts/conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml`。
- [Expanded-bandwidth proxy]：`MMTC_N_RB_DL=51`；是否可精確稱為 20 MHz 仍標為 `[Needs Verification]`。
- [No CSI/SRS workaround]：保留 `MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0"`。
- [iperf]：保留 `MMTC_IPERF_ENABLE=0`；在本 gate 中 iperf 只當 diagnostic。

| Profile 欄位 | 契約 |
|---|---|
| `MMTC_TOTAL_UES_TARGET` | `56`；stage-scan 目標 |
| `MMTC_STAGE_LIST` | `56`；啟動完整支援 stage |
| `MMTC_ACTIVE_UES` | 底層 smoke-run selector；不可重複且範圍為 `1..56` |
| `MMTC_START_XAPP` | baseline 為 `0`；dApp/xApp-enabled comparison 為 `1` |
| `OAI_REDCAP_DAPP_GATE_D_MARKER` | baseline 為 `0`；設成 `1` 啟用 Gate D scheduler marker hooks |
| `MMTC_N_RB_DL` | `51`；expanded-bandwidth proxy `[Needs Verification]` |

`MMTC_ACTIVATE_UE` 不是目前變數。實驗設定檔 v1 不支援多 gNB 或 CU/DU split。

## Baseline Run

```bash
MMTC_REBUILD_IMAGES_BEFORE_SCAN=0 \
MMTC_TOTAL_UES_TARGET=56 \
MMTC_STAGE_LIST=56 \
MMTC_START_XAPP=0 \
MMTC_USE_EXISTING_CN_DB=0 \
MMTC_N_RB_DL=51 \
GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml \
OAI_REDCAP_DAPP_GATE_D_MARKER=0 \
MMTC_IPERF_ENABLE=0 \
MMTC_SLEEP_AFTER_UP=90 \
MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0" \
bash redcap_interface/redcap_mmtc_stage_scan.sh
```

預期產物：

- `test_log/compiler_logs/mmtc_stage_scan_<timestamp>_summary.log`
- `test_log/compiler_logs/mmtc_smoke_<timestamp>_access_latency.csv`

## dApp Enabled Run

```bash
MMTC_REBUILD_IMAGES_BEFORE_SCAN=0 \
MMTC_TOTAL_UES_TARGET=56 \
MMTC_STAGE_LIST=56 \
MMTC_START_XAPP=1 \
MMTC_USE_EXISTING_CN_DB=0 \
MMTC_N_RB_DL=51 \
GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml \
OAI_REDCAP_DAPP_GATE_D_MARKER=1 \
MMTC_IPERF_ENABLE=0 \
MMTC_SLEEP_AFTER_UP=90 \
MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0" \
bash redcap_interface/redcap_mmtc_stage_scan.sh
```

預期產物：

- `test_log/compiler_logs/mmtc_stage_scan_<timestamp>_summary.log`
- `test_log/compiler_logs/mmtc_smoke_<timestamp>_access_latency.csv`
- `test_log/compiler_logs/mmtc_smoke_<timestamp>_gnb.log`

## Evidence Check

使用 2026-07-09 已接受的具體 artifacts：

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_e_64ue_stage_check.py \
  --stage core56-ab \
  --baseline-summary-log test_log/compiler_logs/mmtc_stage_scan_2026-07-09_10-27-10_summary.log \
  --dapp-summary-log test_log/compiler_logs/mmtc_stage_scan_2026-07-09_10-42-43_summary.log \
  --baseline-latency-log test_log/compiler_logs/mmtc_smoke_2026-07-09_10-27-10_access_latency.csv \
  --dapp-latency-log test_log/compiler_logs/mmtc_smoke_2026-07-09_10-42-43_access_latency.csv \
  --dapp-gnb-log test_log/compiler_logs/mmtc_smoke_2026-07-09_10-42-43_gnb.log
```

預期 checker 結果：

- `[PASS] Gate E-Core 56 UE A/B latency evidence found`

## Accepted Result

| Run | sample | running | attach | pdu | tun | forward_ping_ok | gnb_restart | failures |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 56 | 56 | 56 | 56 | 56 | 56 | 0 | 0 |
| dApp Enabled | 56 | 56 | 56 | 56 | 56 | 56 | 0 | 0 |

| Run | Success Count | Median ms | p95 ms | Max ms |
|---|---:|---:|---:|---:|
| Baseline | 56 | 436318 | 703145 | 722926 |
| dApp Enabled | 56 | 441487 | 708146 | 728189 |
| dApp minus Baseline | 0 | +5169 | +5001 | +5263 |

## Expected Markers

- [dApp marker]：dApp-enabled gNB log 需出現 `RedCap dApp PRB decision`。
- [Crash scan]：checker 不得偵測到 `Assertion`、`Aborted` 或 `segfault`。
- [Summary health]：兩份 summary log 都必須回報 `sample=56`、`running=56`、`attach=56`、`pdu=56`、`tun=56`、`gnb_restart=0`、`failures=0`。
- [Latency rows]：兩份 latency CSV 都必須有 56 筆成功的 Launch-to-TUN row。

## dApp/xApp 對齊

| 實驗開關或證據 | 函式路徑 | 已證明效果 |
|---|---|---|
| 啟用 Gate D marker | gNB PUCCH/UL scheduler hook 呼叫 `redcap_dapp_guard_prb_allocation` | Guard 會執行並記錄 `RedCap dApp PRB decision`；是否修改 allocation 為 `[Needs Verification]` |
| 啟用 xApp process | FlexRIC RC monitor/control route | 啟動設定的 xApp 路徑；56 UE A/B artifacts 不證明每個 UE 都收到 RC control |
| 獨立 one-RNTI control evidence | `redcap_xapp_make_ul_prb_ctrl_req` 到 `apply_redcap_ul_prb_control` | 此 A/B timestamp 之外已有 RC ACK 與 gNB apply marker |
| Priority-hint helpers | `redcap_xapp_make_priority_hint` / `redcap_xapp_select_top_priority_hint` | `Public`；production caller 與 apply point 為 `[Needs Verification]` |

## Interpretation

- [Gate E-Core Status]：SDK v1 工程完成門檻 PASS。
- [dApp Latency Claim]：不宣稱改善延遲；本次接受結果中 dApp-enabled run 略慢。
- [xApp Boundary]：56 UE wrapper run 有啟動 `xapp-rc-moni_redcap`，但該 timestamp 沒有額外保存 standalone xApp/RIC logs。
- [Control Path Boundary]：one-RNTI xApp/RIC/gNB control ACK/apply 證據存在，但它是 56 UE A/B 比較之外的獨立證據。
- [Stretch Boundary]：64 UE strict validation 仍屬於 [Gate E-Stretch]，不阻塞 SDK v1 文件化。

## 失敗邊界與保留證據

| 失敗狀況 | 報告方式 |
|---|---|
| 任一 run 少於 56 筆 attach/PDU/TUN | A/B 重現失敗；回報第一個數量不相等的邊界 |
| `gnb_restart` 非零或 crash scan 命中 | Runtime health 失敗 |
| dApp log 缺少 `RedCap dApp PRB decision` | dApp marker evidence 失敗 |
| 兩個 run 都通過但 dApp latency 沒有降低 | 有效 comparison，不是 improvement evidence |
| xApp 已啟動但沒有保留 ACK/apply marker | 該次 run 的 xApp runtime control 維持 `[Needs Verification]` |

保留兩份 summary logs、兩份 latency CSV、dApp gNB log 與 checker output 原有的 `test_log/compiler_logs/` 路徑。不要用 raw logs 取代 accepted report。

## 下一步

使用 [SDK 開發指南](./sdk_development_guide.zh-TW.md) 追蹤或擴充控制函式。行為變更後重新執行相同 A/B profile；不可拿 2026-07-09 accepted evidence 證明新程式碼。
